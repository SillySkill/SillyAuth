"""
Arena Module - Services

Business logic for arena PK battles including room management,
battle orchestration, and ranking calculations.
"""

import logging
import uuid
import math
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum

from psycopg2.extras import RealDictCursor

from .schemas import (
    RoomCreate, RoomResponse, ParticipantInfo,
    RoomStatus, BattleStatus, BattleQuestion,
    BattleResponse, BattleResultResponse, BattleReward,
    ArenaRanking, BattleHistoryEntry
)

logger = logging.getLogger(__name__)


# ============== ELO Rating Calculator ==============

class ELOCalculator:
    """Helper class for ELO rating calculations"""

    @staticmethod
    def calculate_expected_score(rating_a: float, rating_b: float) -> float:
        """
        Calculate expected score for player A against player B.

        Args:
            rating_a: Rating of player A
            rating_b: Rating of player B

        Returns:
            Expected score between 0 and 1
        """
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    @staticmethod
    def calculate_new_ratings(
        winner_rating: int,
        loser_rating: int,
        k_factor: int = 32
    ) -> Tuple[int, int]:
        """
        Calculate new ELO ratings after a match.

        Args:
            winner_rating: Winner's current rating
            loser_rating: Loser's current rating
            k_factor: K-factor for rating volatility (default 32)

        Returns:
            Tuple of (new_winner_rating, new_loser_rating)
        """
        expected_winner = ELOCalculator.calculate_expected_score(winner_rating, loser_rating)
        expected_loser = ELOCalculator.calculate_expected_score(loser_rating, winner_rating)

        new_winner_rating = winner_rating + int(k_factor * (1 - expected_winner))
        new_loser_rating = loser_rating + int(k_factor * (0 - expected_loser))

        return new_winner_rating, new_loser_rating


# ============== Arena Service ==============

class ArenaService:
    """
    Service for managing arena rooms.

    Handles room creation, joining, leaving, and listing operations.
    """

    def __init__(self, db_config: dict, config: dict):
        """
        Initialize arena service.

        Args:
            db_config: Database connection configuration
            config: Module configuration dictionary
        """
        self.db_config = db_config
        self.config = config
        self.max_room_participants = config.get('max_room_participants', 4)

    def _get_db_connection(self):
        """Get a database connection using the configured settings."""
        import psycopg2
        return psycopg2.connect(
            host=self.db_config["host"],
            port=self.db_config["port"],
            database=self.db_config["database"],
            user=self.db_config["user"],
            password=self.db_config["password"]
        )

    def _row_to_room_response(self, row: dict, participants: List[dict] = None) -> RoomResponse:
        """Convert a database row to RoomResponse schema."""
        participant_infos = []
        if participants:
            for p in participants:
                participant_infos.append(ParticipantInfo(
                    user_id=p['user_id'],
                    username=p.get('username', 'Unknown'),
                    elo_rating=p.get('elo_rating', 1000),
                    is_ready=p.get('is_ready', False)
                ))

        return RoomResponse(
            id=row['id'],
            name=row['name'],
            description=row.get('description'),
            status=RoomStatus(row['status']),
            participants=participant_infos,
            max_participants=row['max_participants'],
            is_private=row.get('is_private', False),
            created_by=row['created_by'],
            created_at=row['created_at']
        )

    def create_room(self, creator_id: str, data: RoomCreate) -> RoomResponse:
        """
        Create a new arena room.

        Args:
            creator_id: User ID of the room creator
            data: Room creation data

        Returns:
            Created room information

        Raises:
            Exception: If room creation fails
        """
        import psycopg2

        room_id = f"room_{uuid.uuid4().hex[:12]}"
        now = datetime.now()

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Insert room
                    cur.execute("""
                        INSERT INTO arena_rooms (id, name, description, status, max_participants, is_private, created_by, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id, name, description, status, max_participants, is_private, created_by, created_at
                    """, (
                        room_id,
                        data.name,
                        data.description,
                        RoomStatus.WAITING.value,
                        data.max_participants,
                        data.is_private,
                        creator_id,
                        now
                    ))
                    row = cur.fetchone()

                    # Add creator as participant
                    cur.execute("""
                        INSERT INTO arena_room_participants (room_id, user_id, is_ready, joined_at)
                        VALUES (%s, %s, FALSE, %s)
                    """, (room_id, creator_id, now))

                    conn.commit()

                    # Get participants
                    cur.execute("""
                        SELECT p.user_id, u.username, COALESCE(r.elo_rating, 1000) as elo_rating, p.is_ready
                        FROM arena_room_participants p
                        LEFT JOIN users u ON p.user_id = u.id
                        LEFT JOIN arena_rankings r ON p.user_id = r.user_id
                        WHERE p.room_id = %s
                        ORDER BY p.joined_at
                    """, (room_id,))
                    participants = cur.fetchall()

                    return self._row_to_room_response(row, participants)

        except psycopg2.Error as e:
            logger.error(f"Database error creating room: {e}")
            raise

    def join_room(self, room_id: str, user_id: str) -> RoomResponse:
        """
        Join an existing arena room.

        Args:
            room_id: Room ID to join
            user_id: User ID joining the room

        Returns:
            Updated room information

        Raises:
            ValueError: If room not found or full
            Exception: If operation fails
        """
        import psycopg2

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Check if room exists and get details
                    cur.execute("""
                        SELECT id, name, description, status, max_participants, is_private, created_by, created_at
                        FROM arena_rooms
                        WHERE id = %s
                    """, (room_id,))
                    row = cur.fetchone()

                    if not row:
                        raise ValueError(f"Room {room_id} not found")

                    if row['status'] != RoomStatus.WAITING.value:
                        raise ValueError("Room is not accepting new participants")

                    # Count current participants
                    cur.execute("SELECT COUNT(*) as count FROM arena_room_participants WHERE room_id = %s", (room_id,))
                    count = cur.fetchone()['count']

                    if count >= row['max_participants']:
                        raise ValueError("Room is full")

                    # Add participant
                    cur.execute("""
                        INSERT INTO arena_room_participants (room_id, user_id, is_ready, joined_at)
                        VALUES (%s, %s, FALSE, %s)
                        ON CONFLICT (room_id, user_id) DO NOTHING
                    """, (room_id, user_id, datetime.now()))

                    # Update room status if full
                    if count + 1 >= row['max_participants']:
                        cur.execute("UPDATE arena_rooms SET status = %s WHERE id = %s",
                                  (RoomStatus.READY.value, room_id))
                        row['status'] = RoomStatus.READY.value

                    conn.commit()

                    # Get all participants
                    cur.execute("""
                        SELECT p.user_id, u.username, COALESCE(r.elo_rating, 1000) as elo_rating, p.is_ready
                        FROM arena_room_participants p
                        LEFT JOIN users u ON p.user_id = u.id
                        LEFT JOIN arena_rankings r ON p.user_id = r.user_id
                        WHERE p.room_id = %s
                        ORDER BY p.joined_at
                    """, (room_id,))
                    participants = cur.fetchall()

                    return self._row_to_room_response(row, participants)

        except psycopg2.IntegrityError:
            raise ValueError("Already joined this room")
        except psycopg2.Error as e:
            logger.error(f"Database error joining room: {e}")
            raise

    def leave_room(self, room_id: str, user_id: str) -> bool:
        """
        Leave an arena room.

        Args:
            room_id: Room ID to leave
            user_id: User ID leaving the room

        Returns:
            True if left successfully

        Raises:
            ValueError: If room not found or user not in room
            Exception: If operation fails
        """
        import psycopg2

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Check if room exists
                    cur.execute("SELECT id, status, created_by FROM arena_rooms WHERE id = %s", (room_id,))
                    room = cur.fetchone()

                    if not room:
                        raise ValueError(f"Room {room_id} not found")

                    if room['status'] == RoomStatus.BATTLING.value:
                        raise ValueError("Cannot leave room during battle")

                    # Check if user is in room
                    cur.execute("SELECT 1 FROM arena_room_participants WHERE room_id = %s AND user_id = %s",
                              (room_id, user_id))
                    if not cur.fetchone():
                        raise ValueError("Not a participant of this room")

                    # Remove participant
                    cur.execute("DELETE FROM arena_room_participants WHERE room_id = %s AND user_id = %s",
                              (room_id, user_id))

                    # If creator leaves, delete the room
                    if room['created_by'] == user_id:
                        cur.execute("DELETE FROM arena_rooms WHERE id = %s", (room_id,))
                    else:
                        # Update room status back to waiting if was ready
                        if room['status'] == RoomStatus.READY.value:
                            cur.execute("UPDATE arena_rooms SET status = %s WHERE id = %s",
                                      (RoomStatus.WAITING.value, room_id))

                    conn.commit()
                    return True

        except psycopg2.Error as e:
            logger.error(f"Database error leaving room: {e}")
            raise

    def get_room(self, room_id: str) -> Optional[RoomResponse]:
        """
        Get room details by ID.

        Args:
            room_id: Room ID to retrieve

        Returns:
            Room information or None if not found
        """
        import psycopg2

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, name, description, status, max_participants, is_private, created_by, created_at
                        FROM arena_rooms
                        WHERE id = %s
                    """, (room_id,))
                    row = cur.fetchone()

                    if not row:
                        return None

                    # Get participants
                    cur.execute("""
                        SELECT p.user_id, u.username, COALESCE(r.elo_rating, 1000) as elo_rating, p.is_ready
                        FROM arena_room_participants p
                        LEFT JOIN users u ON p.user_id = u.id
                        LEFT JOIN arena_rankings r ON p.user_id = r.user_id
                        WHERE p.room_id = %s
                        ORDER BY p.joined_at
                    """, (room_id,))
                    participants = cur.fetchall()

                    return self._row_to_room_response(row, participants)

        except psycopg2.Error as e:
            logger.error(f"Database error getting room: {e}")
            raise

    def list_rooms(self, status: Optional[RoomStatus] = None, page: int = 1, limit: int = 20) -> Tuple[List[RoomResponse], int]:
        """
        List arena rooms with pagination.

        Args:
            status: Optional status filter
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Tuple of (list of rooms, total count)
        """
        import psycopg2

        offset = (page - 1) * limit

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Build query
                    where_clause = ""
                    params = []

                    if status:
                        where_clause = "WHERE r.status = %s"
                        params.append(status.value)

                    # Get total count
                    count_query = f"SELECT COUNT(*) as count FROM arena_rooms r {where_clause}"
                    cur.execute(count_query, params)
                    total = cur.fetchone()['count']

                    # Get rooms
                    query = f"""
                        SELECT r.id, r.name, r.description, r.status, r.max_participants, r.is_private, r.created_by, r.created_at
                        FROM arena_rooms r
                        {where_clause}
                        ORDER BY r.created_at DESC
                        LIMIT %s OFFSET %s
                    """
                    cur.execute(query, params + [limit, offset])
                    rows = cur.fetchall()

                    rooms = []
                    for row in rows:
                        # Get participants for each room
                        cur.execute("""
                            SELECT p.user_id, u.username, COALESCE(rank.elo_rating, 1000) as elo_rating, p.is_ready
                            FROM arena_room_participants p
                            LEFT JOIN users u ON p.user_id = u.id
                            LEFT JOIN arena_rankings rank ON p.user_id = rank.user_id
                            WHERE p.room_id = %s
                            ORDER BY p.joined_at
                        """, (row['id'],))
                        participants = cur.fetchall()
                        rooms.append(self._row_to_room_response(row, participants))

                    return rooms, total

        except psycopg2.Error as e:
            logger.error(f"Database error listing rooms: {e}")
            raise

    def initialize_database(self) -> None:
        """
        Initialize the database tables for arena.

        Creates necessary tables if they don't exist.

        Raises:
            Exception: If table creation fails
        """
        import psycopg2

        create_tables_sql = """
        -- Arena rooms table
        CREATE TABLE IF NOT EXISTS arena_rooms (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            description TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'waiting',
            max_participants INTEGER NOT NULL DEFAULT 4,
            is_private BOOLEAN DEFAULT FALSE,
            created_by VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Room participants table
        CREATE TABLE IF NOT EXISTS arena_room_participants (
            room_id VARCHAR(50) NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            is_ready BOOLEAN DEFAULT FALSE,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (room_id, user_id),
            FOREIGN KEY (room_id) REFERENCES arena_rooms(id) ON DELETE CASCADE
        );

        -- Arena rankings table
        CREATE TABLE IF NOT EXISTS arena_rankings (
            user_id VARCHAR(50) PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            elo_rating INTEGER NOT NULL DEFAULT 1000,
            wins INTEGER NOT NULL DEFAULT 0,
            losses INTEGER NOT NULL DEFAULT 0,
            current_streak INTEGER NOT NULL DEFAULT 0,
            best_streak INTEGER NOT NULL DEFAULT 0,
            total_battles INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Battles table
        CREATE TABLE IF NOT EXISTS arena_battles (
            id VARCHAR(50) PRIMARY KEY,
            room_id VARCHAR(50) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            total_questions INTEGER NOT NULL DEFAULT 10,
            current_question INTEGER NOT NULL DEFAULT 0,
            started_at TIMESTAMP,
            ended_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES arena_rooms(id) ON DELETE CASCADE
        );

        -- Battle participants table
        CREATE TABLE IF NOT EXISTS arena_battle_participants (
            battle_id VARCHAR(50) NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            score INTEGER NOT NULL DEFAULT 0,
            is_winner BOOLEAN DEFAULT FALSE,
            elo_before INTEGER NOT NULL,
            elo_after INTEGER NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (battle_id, user_id),
            FOREIGN KEY (battle_id) REFERENCES arena_battles(id) ON DELETE CASCADE
        );

        -- Battle answers table
        CREATE TABLE IF NOT EXISTS arena_battle_answers (
            id SERIAL PRIMARY KEY,
            battle_id VARCHAR(50) NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            question_index INTEGER NOT NULL,
            answer VARCHAR(500),
            is_correct BOOLEAN,
            time_taken FLOAT,
            points_earned INTEGER DEFAULT 0,
            answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (battle_id) REFERENCES arena_battles(id) ON DELETE CASCADE
        );

        -- Battle history table
        CREATE TABLE IF NOT EXISTS arena_battle_history (
            id SERIAL PRIMARY KEY,
            battle_id VARCHAR(50) NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            opponent_id VARCHAR(50) NOT NULL,
            result VARCHAR(10) NOT NULL,
            my_score INTEGER NOT NULL,
            opponent_score INTEGER NOT NULL,
            elo_change INTEGER NOT NULL,
            new_elo INTEGER NOT NULL,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_arena_rooms_status ON arena_rooms(status);
        CREATE INDEX IF NOT EXISTS idx_arena_rooms_created_at ON arena_rooms(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_arena_rankings_elo ON arena_rankings(elo_rating DESC);
        CREATE INDEX IF NOT EXISTS idx_arena_battles_room_id ON arena_battles(room_id);
        CREATE INDEX IF NOT EXISTS idx_arena_battles_status ON arena_battles(status);
        CREATE INDEX IF NOT EXISTS idx_arena_battle_history_user_id ON arena_battle_history(user_id);
        CREATE INDEX IF NOT EXISTS idx_arena_battle_history_played_at ON arena_battle_history(played_at DESC);
        """

        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_tables_sql)
                    conn.commit()
                    logger.info("Arena database tables initialized successfully")

        except psycopg2.Error as e:
            logger.error(f"Database error initializing arena tables: {e}")
            raise


# ============== Battle Service ==============

class BattleService:
    """
    Service for managing battles.

    Handles battle creation, answer submission, and battle completion.
    """

    def __init__(self, db_config: dict, config: dict):
        """
        Initialize battle service.

        Args:
            db_config: Database connection configuration
            config: Module configuration dictionary
        """
        self.db_config = db_config
        self.config = config
        self.battle_timeout = config.get('battle_timeout_seconds', 300)
        self.elo_k_factor = config.get('elo_k_factor', 32)
        self.initial_elo = config.get('initial_elo_rating', 1000)

    def _get_db_connection(self):
        """Get a database connection using the configured settings."""
        import psycopg2
        return psycopg2.connect(
            host=self.db_config["host"],
            port=self.db_config["port"],
            database=self.db_config["database"],
            user=self.db_config["user"],
            password=self.db_config["password"]
        )

    def start_battle(self, room_id: str, participant_ids: List[str]) -> BattleResponse:
        """
        Start a battle in a room.

        Args:
            room_id: Room ID to start battle in
            participant_ids: List of participant user IDs

        Returns:
            Battle information

        Raises:
            ValueError: If room not found or invalid state
            Exception: If operation fails
        """
        import psycopg2

        battle_id = f"battle_{uuid.uuid4().hex[:12]}"
        now = datetime.now()
        ends_at = now + timedelta(seconds=self.battle_timeout)

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Check room exists and is ready
                    cur.execute("SELECT id, status FROM arena_rooms WHERE id = %s", (room_id,))
                    room = cur.fetchone()

                    if not room:
                        raise ValueError(f"Room {room_id} not found")

                    if room['status'] != RoomStatus.READY.value:
                        raise ValueError("Room is not ready for battle")

                    # Update room status
                    cur.execute("UPDATE arena_rooms SET status = %s WHERE id = %s",
                              (RoomStatus.BATTLING.value, room_id))

                    # Create battle
                    cur.execute("""
                        INSERT INTO arena_battles (id, room_id, status, total_questions, started_at)
                        VALUES (%s, %s, %s, 10, %s)
                        RETURNING id, room_id, status, total_questions, current_question, started_at
                    """, (battle_id, room_id, BattleStatus.IN_PROGRESS.value, now))
                    battle_row = cur.fetchone()

                    # Add participants with their ELO ratings
                    for user_id in participant_ids:
                        cur.execute("""
                            SELECT COALESCE(elo_rating, %s) as elo_rating
                            FROM arena_rankings
                            WHERE user_id = %s
                        """, (self.initial_elo, user_id))
                        result = cur.fetchone()
                        elo = result['elo_rating'] if result else self.initial_elo

                        cur.execute("""
                            INSERT INTO arena_battle_participants (battle_id, user_id, elo_before, elo_after)
                            VALUES (%s, %s, %s, %s)
                        """, (battle_id, user_id, elo, elo))

                    conn.commit()

                    # Get participant info
                    cur.execute("""
                        SELECT p.user_id, u.username, COALESCE(r.elo_rating, %s) as elo_rating, FALSE as is_ready
                        FROM arena_battle_participants p
                        LEFT JOIN users u ON p.user_id = u.id
                        LEFT JOIN arena_rankings r ON p.user_id = r.user_id
                        WHERE p.battle_id = %s
                        ORDER BY p.joined_at
                    """, (self.initial_elo, battle_id))
                    participants = cur.fetchall()

                    participant_infos = [
                        ParticipantInfo(
                            user_id=p['user_id'],
                            username=p.get('username', 'Unknown'),
                            elo_rating=p.get('elo_rating', self.initial_elo),
                            is_ready=p.get('is_ready', False)
                        ) for p in participants
                    ]

                    return BattleResponse(
                        battle_id=battle_row['id'],
                        room_id=battle_row['room_id'],
                        status=BattleStatus(battle_row['status']),
                        participants=participant_infos,
                        current_question=None,
                        question_index=battle_row['current_question'],
                        total_questions=battle_row['total_questions'],
                        started_at=battle_row['started_at'],
                        ends_at=ends_at
                    )

        except psycopg2.Error as e:
            logger.error(f"Database error starting battle: {e}")
            raise

    def submit_answer(self, battle_id: str, user_id: str, answer: str, time_taken: float,
                     correct_answer: str, points_per_question: int = 100) -> Dict[str, Any]:
        """
        Submit an answer for a battle question.

        Args:
            battle_id: Battle ID
            user_id: User ID submitting the answer
            answer: The submitted answer
            time_taken: Time taken to answer in seconds
            correct_answer: The correct answer for scoring
            points_per_question: Points awarded for correct answer

        Returns:
            Answer result with scoring information

        Raises:
            ValueError: If battle not found or invalid state
            Exception: If operation fails
        """
        import psycopg2

        now = datetime.now()

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Check battle exists and is in progress
                    cur.execute("""
                        SELECT id, status, current_question, total_questions, started_at
                        FROM arena_battles
                        WHERE id = %s
                    """, (battle_id,))
                    battle = cur.fetchone()

                    if not battle:
                        raise ValueError(f"Battle {battle_id} not found")

                    if battle['status'] != BattleStatus.IN_PROGRESS.value:
                        raise ValueError("Battle is not in progress")

                    # Check if user is participant
                    cur.execute("""
                        SELECT user_id, score FROM arena_battle_participants
                        WHERE battle_id = %s AND user_id = %s
                    """, (battle_id, user_id))
                    participant = cur.fetchone()

                    if not participant:
                        raise ValueError("Not a participant of this battle")

                    # Check if already answered this question
                    cur.execute("""
                        SELECT 1 FROM arena_battle_answers
                        WHERE battle_id = %s AND user_id = %s AND question_index = %s
                    """, (battle_id, user_id, battle['current_question']))
                    if cur.fetchone():
                        raise ValueError("Already answered this question")

                    # Check answer correctness
                    is_correct = (answer.strip().upper() == correct_answer.strip().upper())
                    points_earned = points_per_question if is_correct else 0

                    # Time bonus (faster = more points, max 50% bonus)
                    if is_correct and time_taken < 30:
                        time_bonus = int(points_per_question * 0.5 * (1 - time_taken / 30))
                        points_earned += time_bonus

                    # Record answer
                    cur.execute("""
                        INSERT INTO arena_battle_answers
                        (battle_id, user_id, question_index, answer, is_correct, time_taken, points_earned)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (battle_id, user_id, battle['current_question'], answer,
                          is_correct, time_taken, points_earned))

                    # Update participant score
                    new_score = participant['score'] + points_earned
                    cur.execute("""
                        UPDATE arena_battle_participants
                        SET score = %s
                        WHERE battle_id = %s AND user_id = %s
                    """, (new_score, battle_id, user_id))

                    # Move to next question
                    next_question = battle['current_question'] + 1
                    if next_question >= battle['total_questions']:
                        # Battle finished
                        cur.execute("""
                            UPDATE arena_battles
                            SET status = %s, ended_at = %s
                            WHERE id = %s
                        """, (BattleStatus.FINISHED.value, now, battle_id))
                    else:
                        cur.execute("""
                            UPDATE arena_battles
                            SET current_question = %s
                            WHERE id = %s
                        """, (next_question, battle_id))

                    conn.commit()

                    return {
                        "correct": is_correct,
                        "correct_answer": correct_answer if not is_correct else None,
                        "points_earned": points_earned,
                        "total_points": new_score
                    }

        except psycopg2.Error as e:
            logger.error(f"Database error submitting answer: {e}")
            raise

    def finish_battle(self, battle_id: str) -> BattleResultResponse:
        """
        Finish a battle and calculate results.

        Args:
            battle_id: Battle ID to finish

        Returns:
            Battle result with winner, scores, and rewards

        Raises:
            ValueError: If battle not found or not finished
            Exception: If operation fails
        """
        import psycopg2

        now = datetime.now()

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get battle info
                    cur.execute("""
                        SELECT id, room_id, status FROM arena_battles WHERE id = %s
                    """, (battle_id,))
                    battle = cur.fetchone()

                    if not battle:
                        raise ValueError(f"Battle {battle_id} not found")

                    if battle['status'] != BattleStatus.FINISHED.value:
                        raise ValueError("Battle is not finished yet")

                    # Get participants and their scores
                    cur.execute("""
                        SELECT bp.user_id, u.username, bp.score, bp.elo_before
                        FROM arena_battle_participants bp
                        LEFT JOIN users u ON bp.user_id = u.id
                        WHERE bp.battle_id = %s
                        ORDER BY bp.score DESC
                    """, (battle_id,))
                    participants = cur.fetchall()

                    if len(participants) < 2:
                        raise ValueError("Not enough participants for battle result")

                    # Sort by score
                    sorted_participants = sorted(participants, key=lambda x: x['score'], reverse=True)
                    winner = sorted_participants[0]
                    loser = sorted_participants[1]

                    # Calculate ELO changes
                    new_winner_elo, new_loser_elo = ELOCalculator.calculate_new_ratings(
                        winner['elo_before'],
                        loser['score'],
                        self.elo_k_factor
                    )

                    # Update ELO ratings
                    cur.execute("""
                        UPDATE arena_battle_participants
                        SET elo_after = %s, is_winner = TRUE
                        WHERE battle_id = %s AND user_id = %s
                    """, (new_winner_elo, battle_id, winner['user_id']))

                    cur.execute("""
                        UPDATE arena_battle_participants
                        SET elo_after = %s
                        WHERE battle_id = %s AND user_id = %s
                    """, (new_loser_elo, battle_id, loser['user_id']))

                    # Update rankings
                    elo_change_winner = new_winner_elo - winner['elo_before']
                    elo_change_loser = new_loser_elo - loser['elo_before']

                    # Update or create winner ranking
                    cur.execute("""
                        INSERT INTO arena_rankings (user_id, username, elo_rating, wins, current_streak, best_streak, total_battles, updated_at)
                        VALUES (%s, %s, %s, 1, 1,
                            CASE WHEN 1 > (SELECT COALESCE(best_streak, 0) FROM arena_rankings WHERE user_id = %s) THEN 1
                                 ELSE (SELECT COALESCE(best_streak, 0) FROM arena_rankings WHERE user_id = %s) END,
                            1, %s)
                        ON CONFLICT (user_id) DO UPDATE SET
                            elo_rating = arena_rankings.elo_rating + %s,
                            wins = arena_rankings.wins + 1,
                            current_streak = arena_rankings.current_streak + 1,
                            best_streak = GREATEST(arena_rankings.best_streak, arena_rankings.current_streak + 1),
                            total_battles = arena_rankings.total_battles + 1,
                            updated_at = %s
                    """, (winner['user_id'], winner['username'], new_winner_elo,
                          winner['user_id'], winner['user_id'], now,
                          elo_change_winner, now))

                    # Update or create loser ranking
                    cur.execute("""
                        INSERT INTO arena_rankings (user_id, username, elo_rating, losses, current_streak, best_streak, total_battles, updated_at)
                        VALUES (%s, %s, %s, 1, -1, 0, 1, %s)
                        ON CONFLICT (user_id) DO UPDATE SET
                            elo_rating = arena_rankings.elo_rating + %s,
                            losses = arena_rankings.losses + 1,
                            current_streak = arena_rankings.current_streak - 1,
                            total_battles = arena_rankings.total_battles + 1,
                            updated_at = %s
                    """, (loser['user_id'], loser['username'], new_loser_elo, now,
                          elo_change_loser, now))

                    # Record battle history for each participant
                    # Winner
                    cur.execute("""
                        INSERT INTO arena_battle_history
                        (battle_id, user_id, opponent_id, result, my_score, opponent_score, elo_change, new_elo, played_at)
                        VALUES (%s, %s, %s, 'WIN', %s, %s, %s, %s, %s)
                    """, (battle_id, winner['user_id'], loser['user_id'],
                          winner['score'], loser['score'], elo_change_winner, new_winner_elo, now))

                    # Loser
                    cur.execute("""
                        INSERT INTO arena_battle_history
                        (battle_id, user_id, opponent_id, result, my_score, opponent_score, elo_change, new_elo, played_at)
                        VALUES (%s, %s, %s, 'LOSE', %s, %s, %s, %s, %s)
                    """, (battle_id, loser['user_id'], winner['user_id'],
                          loser['score'], winner['score'], elo_change_loser, new_loser_elo, now))

                    # Update room status
                    cur.execute("""
                        UPDATE arena_rooms SET status = %s WHERE id = %s
                    """, (RoomStatus.FINISHED.value, battle['room_id']))

                    conn.commit()

                    # Calculate rewards
                    rewards = {
                        winner['user_id']: BattleReward(
                            experience=100 + (elo_change_winner * 2),
                            coins=50 + elo_change_winner,
                            rating_change=elo_change_winner
                        ).model_dump(),
                        loser['user_id']: BattleReward(
                            experience=50 + abs(elo_change_loser),
                            coins=25 + abs(elo_change_loser),
                            rating_change=elo_change_loser
                        ).model_dump()
                    }

                    scores = {p['user_id']: p['score'] for p in sorted_participants}
                    elo_changes = {
                        winner['user_id']: elo_change_winner,
                        loser['user_id']: elo_change_loser
                    }

                    return BattleResultResponse(
                        battle_id=battle_id,
                        winner_id=winner['user_id'],
                        winner_name=winner.get('username', 'Unknown'),
                        loser_id=loser['user_id'],
                        loser_name=loser.get('username', 'Unknown'),
                        score=scores,
                        rewards=rewards,
                        elo_changes=elo_changes,
                        finished_at=now
                    )

        except psycopg2.Error as e:
            logger.error(f"Database error finishing battle: {e}")
            raise

    def get_battle_history(self, user_id: str, page: int = 1, limit: int = 20) -> Tuple[List[BattleHistoryEntry], int]:
        """
        Get battle history for a user.

        Args:
            user_id: User ID to get history for
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Tuple of (list of battle history entries, total count)
        """
        import psycopg2

        offset = (page - 1) * limit

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get total count
                    cur.execute("""
                        SELECT COUNT(*) as count FROM arena_battle_history WHERE user_id = %s
                    """, (user_id,))
                    total = cur.fetchone()['count']

                    # Get history
                    cur.execute("""
                        SELECT
                            h.battle_id,
                            r.name as room_name,
                            h.opponent_id,
                            u.username as opponent_name,
                            h.result,
                            h.my_score,
                            h.opponent_score,
                            h.elo_change,
                            h.new_elo,
                            h.played_at
                        FROM arena_battle_history h
                        LEFT JOIN arena_battles b ON h.battle_id = b.id
                        LEFT JOIN arena_rooms r ON b.room_id = r.id
                        LEFT JOIN users u ON h.opponent_id = u.id
                        WHERE h.user_id = %s
                        ORDER BY h.played_at DESC
                        LIMIT %s OFFSET %s
                    """, (user_id, limit, offset))
                    rows = cur.fetchall()

                    battles = [
                        BattleHistoryEntry(
                            battle_id=row['battle_id'],
                            room_name=row['room_name'] or 'Unknown Room',
                            opponent_id=row['opponent_id'],
                            opponent_name=row.get('opponent_name', 'Unknown'),
                            result=row['result'],
                            my_score=row['my_score'],
                            opponent_score=row['opponent_score'],
                            elo_change=row['elo_change'],
                            new_elo=row['new_elo'],
                            played_at=row['played_at']
                        ) for row in rows
                    ]

                    return battles, total

        except psycopg2.Error as e:
            logger.error(f"Database error getting battle history: {e}")
            raise


# ============== Ranking Service ==============

class RankingService:
    """
    Service for managing arena rankings.

    Handles ranking retrieval and ELO calculations.
    """

    def __init__(self, db_config: dict, config: dict):
        """
        Initialize ranking service.

        Args:
            db_config: Database connection configuration
            config: Module configuration dictionary
        """
        self.db_config = db_config
        self.config = config
        self.elo_k_factor = config.get('elo_k_factor', 32)

    def _get_db_connection(self):
        """Get a database connection using the configured settings."""
        import psycopg2
        return psycopg2.connect(
            host=self.db_config["host"],
            port=self.db_config["port"],
            database=self.db_config["database"],
            user=self.db_config["user"],
            password=self.db_config["password"]
        )

    def get_rankings(self, page: int = 1, limit: int = 20) -> Tuple[List[ArenaRanking], int]:
        """
        Get arena rankings with pagination.

        Args:
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Tuple of (list of rankings, total count)
        """
        import psycopg2

        offset = (page - 1) * limit

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get total count
                    cur.execute("SELECT COUNT(*) as count FROM arena_rankings")
                    total = cur.fetchone()['count']

                    # Get rankings
                    cur.execute("""
                        SELECT
                            user_id,
                            username,
                            elo_rating,
                            wins,
                            losses,
                            total_battles,
                            current_streak
                        FROM arena_rankings
                        ORDER BY elo_rating DESC
                        LIMIT %s OFFSET %s
                    """, (limit, offset))
                    rows = cur.fetchall()

                    rankings = []
                    for idx, row in enumerate(rows):
                        total_games = row['wins'] + row['losses']
                        win_rate = (row['wins'] / total_games * 100) if total_games > 0 else 0.0

                        rankings.append(ArenaRanking(
                            rank=offset + idx + 1,
                            user_id=row['user_id'],
                            username=row.get('username', 'Unknown'),
                            elo_rating=row['elo_rating'],
                            wins=row['wins'],
                            losses=row['losses'],
                            win_rate=round(win_rate, 2),
                            streak=row['current_streak']
                        ))

                    return rankings, total

        except psycopg2.Error as e:
            logger.error(f"Database error getting rankings: {e}")
            raise

    def get_user_rank(self, user_id: str) -> Optional[ArenaRanking]:
        """
        Get ranking information for a specific user.

        Args:
            user_id: User ID to get rank for

        Returns:
            Ranking information or None if user not found
        """
        import psycopg2

        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get user ranking
                    cur.execute("""
                        SELECT
                            user_id,
                            username,
                            elo_rating,
                            wins,
                            losses,
                            total_battles,
                            current_streak
                        FROM arena_rankings
                        WHERE user_id = %s
                    """, (user_id,))
                    row = cur.fetchone()

                    if not row:
                        return None

                    # Calculate rank
                    cur.execute("""
                        SELECT COUNT(*) + 1 as rank
                        FROM arena_rankings
                        WHERE elo_rating > %s
                    """, (row['elo_rating'],))
                    rank = cur.fetchone()['rank']

                    total_games = row['wins'] + row['losses']
                    win_rate = (row['wins'] / total_games * 100) if total_games > 0 else 0.0

                    return ArenaRanking(
                        rank=rank,
                        user_id=row['user_id'],
                        username=row.get('username', 'Unknown'),
                        elo_rating=row['elo_rating'],
                        wins=row['wins'],
                        losses=row['losses'],
                        win_rate=round(win_rate, 2),
                        streak=row['current_streak']
                    )

        except psycopg2.Error as e:
            logger.error(f"Database error getting user rank: {e}")
            raise

    def calculate_elo(self, winner_rating: int, loser_rating: int) -> Tuple[int, int]:
        """
        Calculate new ELO ratings after a match.

        Args:
            winner_rating: Winner's current rating
            loser_rating: Loser's current rating

        Returns:
            Tuple of (new_winner_rating, new_loser_rating)
        """
        return ELOCalculator.calculate_new_ratings(
            winner_rating,
            loser_rating,
            self.elo_k_factor
        )

"""
Upload skills from local directories to TOS and record in database.
"""
import sys, os, io, time, zipfile, logging

# CRITICAL: Clear proxy env vars before importing anything network-related
for k in list(os.environ.keys()):
    if "proxy" in k.lower():
        del os.environ[k]
os.environ["no_proxy"] = "*"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Load env vars from .env
env_path = os.path.join(os.path.dirname(__file__), "src", ".env")
if os.path.exists(env_path):
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.split("#")[0].strip())

os.environ.setdefault("JWT_SECRET", "sillymd-dev-jwt-secret-key-2024")
os.environ.setdefault("DB_HOST", "pgm-bp17g13e3k5y08y1wo.pg.rds.aliyuncs.com")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "sillymd")
os.environ.setdefault("DB_USER", "sillyAdmin")
os.environ.setdefault("DB_PASSWORD", "Jcoding2026")

import tos
from core.db_adapter import get_db_cursor

TOS_BASE_KEY = "skills/skill-packages/"
TOS_CUSTOM_DOMAIN = "resource.sillymd.com"
SKILLS_DIR = r"F:\SillyClaw\resources\openclaw\skills"

ACCESS_KEY = os.getenv("TOS_ACCESS_KEY", "")
SECRET_KEY = os.getenv("TOS_SECRET_KEY", "")
ENDPOINT = os.getenv("TOS_ENDPOINT", "tos-cn-shanghai.volces.com")
BUCKET = os.getenv("TOS_BUCKET", "sillymd")


def make_tos_client():
    """Create a TOS client with proxy disabled."""
    client = tos.TosClientV2(ACCESS_KEY, SECRET_KEY, ENDPOINT, region="cn-shanghai")
    # Disable proxy auto-detection on the internal requests session
    if hasattr(client, "session"):
        client.session.trust_env = False
    return client


def get_skills_without_tos():
    """Get all awesome-complete skills without package_url."""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, name, skill_id, version
            FROM skills
            WHERE (package_url IS NULL OR package_url = '')
              AND is_deleted = FALSE AND source = 'awesome-complete'
            ORDER BY id
        """)
        return cur.fetchall()


def zip_directory(dir_path: str) -> bytes:
    """Zip a directory into bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(dir_path):
            for fname in files:
                file_path = os.path.join(root, fname)
                arcname = os.path.relpath(file_path, dir_path)
                zf.write(file_path, arcname)
    return buf.getvalue()


def upload_to_tos(client, data: bytes, tos_key: str) -> str:
    """Upload bytes to TOS and return the public URL."""
    result = client.put_object(bucket=BUCKET, key=tos_key, content=data, content_type="application/zip")
    url = f"https://{TOS_CUSTOM_DOMAIN}/{tos_key}"
    return url


def main():
    logger.info(f"Initializing TOS client: bucket={BUCKET}, endpoint={ENDPOINT}")
    client = make_tos_client()
    logger.info("TOS client ready")

    skills = get_skills_without_tos()
    logger.info(f"Found {len(skills)} skills without TOS links")

    success = 0
    failed = 0
    skipped = 0

    for skill in skills:
        skill_id_val = skill["skill_id"]
        dirname = skill_id_val.replace("awesome_", "", 1) if skill_id_val.startswith("awesome_") else skill_id_val
        dir_path = os.path.join(SKILLS_DIR, dirname)

        if not os.path.isdir(dir_path):
            logger.warning(f"  [SKIP] ID={skill['id']} {skill['name']}: dir not found: {dir_path}")
            skipped += 1
            continue

        ts = int(time.time())
        version = skill.get("version")
        if version and version != "1.0.0":
            fname = f"{dirname}-{version}-{ts}.zip"
        else:
            fname = f"{dirname}-{ts}.zip"
        tos_key = TOS_BASE_KEY + fname

        try:
            logger.info(f"  [{success+1}/{len(skills)}] ID={skill['id']} {skill['name']} -> {tos_key}")
            zip_data = zip_directory(dir_path)
            upload_url = upload_to_tos(client, zip_data, tos_key)

            with get_db_cursor() as cur:
                cur.execute(
                    "UPDATE skills SET package_url = %s WHERE id = %s",
                    (upload_url, skill["id"]),
                )
            logger.info(f"    OK ({len(zip_data)/1024:.1f} KB)")
            success += 1

        except Exception as e:
            logger.error(f"    FAILED ID={skill['id']}: {e}")
            failed += 1

    logger.info(f"\nDone. Success: {success}, Failed: {failed}, Skipped: {skipped}")


if __name__ == "__main__":
    main()

# 第八章：数字存证架构

> 本文档描述商用 Skills 的数字签名存证机制。
>
> 本章涵盖数字存证架构所需的所有数据库表结构设计。

## 8.0 数据库设计

### 8.0.1 枚举类型定义

```sql
-- ============================================
-- 数字存证系统枚举类型
-- ============================================

CREATE TYPE proof_type AS ENUM ('creation', 'modification', 'transfer', 'verification');
CREATE TYPE verification_status AS ENUM ('pending', 'verified', 'failed', 'expired');
CREATE TYPE signer_type AS ENUM ('author', 'platform', 'notary', 'third_party');
CREATE TYPE blockchain_type AS ENUM ('ethereum', 'bitcoin', 'polygon', 'bsc', 'arweave', 'ipfs', 'custom');
CREATE TYPE blockchain_network AS ENUM ('mainnet', 'testnet', 'private');
CREATE TYPE blockchain_record_status AS ENUM ('pending', 'confirmed', 'failed', 'reverted');
CREATE TYPE verification_type AS ENUM ('integrity', 'signature', 'timestamp', 'blockchain', 'full');
CREATE TYPE verifier_type AS ENUM ('system', 'user', 'admin', 'api');
CREATE TYPE verification_result AS ENUM ('success', 'failed', 'partial', 'error');
```

### 8.0.2 数字存证表 (digital_proofs)

```sql
CREATE TABLE digital_proofs (
    id BIGSERIAL PRIMARY KEY,
    skill_id BIGINT NOT NULL,
    proof_type proof_type NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    content_uri VARCHAR(500),
    proof_data JSONB NOT NULL,
    signature_algorithm VARCHAR(50) NOT NULL DEFAULT 'RSA-2048',
    author_signature VARCHAR(500),
    platform_signature VARCHAR(500) NOT NULL,
    signature_timestamp TIMESTAMPTZ NOT NULL,
    merkle_root VARCHAR(64),
    merkle_path JSONB,
    blockchain_tx_hash VARCHAR(255),
    blockchain_height BIGINT,
    verification_status verification_status NOT NULL DEFAULT 'pending',
    verification_count INT DEFAULT 0,
    last_verified_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (skill_id, content_hash, proof_type),
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_digital_proofs_skill_id ON digital_proofs(skill_id);
CREATE INDEX idx_digital_proofs_content_hash ON digital_proofs(content_hash);
CREATE INDEX idx_digital_proofs_proof_type ON digital_proofs(proof_type);
CREATE INDEX idx_digital_proofs_verification_status ON digital_proofs(verification_status);
CREATE INDEX idx_digital_proofs_blockchain_tx ON digital_proofs(blockchain_tx_hash);
```

### 8.0.3 内容哈希表 (content_hashes)

```sql
CREATE TABLE content_hashes (
    id BIGSERIAL PRIMARY KEY,
    skill_id BIGINT NOT NULL,
    hash_algorithm VARCHAR(20) NOT NULL DEFAULT 'sha256',
    hash_value VARCHAR(128) NOT NULL,
    content_range VARCHAR(100),
    content_size BIGINT,
    content_type VARCHAR(100),
    hash_metadata JSONB,
    is_primary BOOLEAN NOT NULL DEFAULT TRUE,
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (skill_id, hash_value, hash_algorithm),
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_content_hashes_skill_id ON content_hashes(skill_id);
CREATE INDEX idx_content_hashes_hash_value ON content_hashes(hash_value);
CREATE INDEX idx_content_hashes_hash_algorithm ON content_hashes(hash_algorithm);
```

### 8.0.4 数字签名表 (signatures)

```sql
CREATE TABLE signatures (
    id BIGSERIAL PRIMARY KEY,
    proof_id BIGINT NOT NULL,
    skill_id BIGINT NOT NULL,
    signer_type signer_type NOT NULL,
    signer_id BIGINT,
    signer_name VARCHAR(255),
    signature_value TEXT NOT NULL,
    signature_algorithm VARCHAR(50) NOT NULL,
    public_key_fingerprint VARCHAR(255),
    certificate_chain TEXT,
    signature_purpose VARCHAR(255),
    signing_timestamp TIMESTAMPTZ NOT NULL,
    expiry_timestamp TIMESTAMPTZ,
    is_valid BOOLEAN NOT NULL DEFAULT TRUE,
    validation_result JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proof_id) REFERENCES digital_proofs(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_signatures_proof_id ON signatures(proof_id);
CREATE INDEX idx_signatures_skill_id ON signatures(skill_id);
CREATE INDEX idx_signatures_signer_type ON signatures(signer_type);
CREATE INDEX idx_signatures_signer_id ON signatures(signer_id);
CREATE INDEX idx_signatures_is_valid ON signatures(is_valid);
```

### 8.0.5 区块链记录表 (blockchain_records)

```sql
CREATE TABLE blockchain_records (
    id BIGSERIAL PRIMARY KEY,
    proof_id BIGINT NOT NULL,
    blockchain_type blockchain_type NOT NULL,
    network blockchain_network NOT NULL DEFAULT 'mainnet',
    transaction_hash VARCHAR(255) UNIQUE NOT NULL,
    block_number BIGINT,
    block_hash VARCHAR(255),
    block_timestamp TIMESTAMPTZ,
    contract_address VARCHAR(255),
    transaction_index INT,
    gas_used BIGINT,
    gas_price BIGINT,
    transaction_cost NUMERIC(20,8),
    confirmation_count INT DEFAULT 0,
    status blockchain_record_status NOT NULL DEFAULT 'pending',
    metadata JSONB,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMPTZ,
    FOREIGN KEY (proof_id) REFERENCES digital_proofs(id)
);

-- 索引
CREATE INDEX idx_blockchain_records_proof_id ON blockchain_records(proof_id);
CREATE INDEX idx_blockchain_records_blockchain_type ON blockchain_records(blockchain_type);
CREATE INDEX idx_blockchain_records_transaction_hash ON blockchain_records(transaction_hash);
CREATE INDEX idx_blockchain_records_block_number ON blockchain_records(block_number);
CREATE INDEX idx_blockchain_records_status ON blockchain_records(status);
```

### 8.0.6 验证日志表 (verification_logs)

```sql
CREATE TABLE verification_logs (
    id BIGSERIAL PRIMARY KEY,
    proof_id BIGINT NOT NULL,
    skill_id BIGINT NOT NULL,
    verification_type verification_type NOT NULL,
    verifier_type verifier_type NOT NULL,
    verifier_id BIGINT,
    verification_method VARCHAR(100),
    verification_result verification_result NOT NULL,
    verification_details JSONB,
    checks_performed JSONB,
    error_message TEXT,
    verification_duration INT,
    client_ip VARCHAR(45),
    user_agent VARCHAR(500),
    verified_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proof_id) REFERENCES digital_proofs(id),
    FOREIGN KEY (skill_id) REFERENCES skills(id)
);

-- 索引
CREATE INDEX idx_verification_logs_proof_id ON verification_logs(proof_id);
CREATE INDEX idx_verification_logs_skill_id ON verification_logs(skill_id);
CREATE INDEX idx_verification_logs_verification_type ON verification_logs(verification_type);
CREATE INDEX idx_verification_logs_verification_result ON verification_logs(verification_result);
CREATE INDEX idx_verification_logs_verified_at ON verification_logs(verified_at);
```

### 8.0.7 数据表关系图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        数字存证系统数据库关系图                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐                                                       │
│  │   skills     │                                                       │
│  │              │                                                       │
│  │ - id         │                                                       │
│  └──────┬───────┘                                                       │
│         │                                                                 │
│         v                                                                 │
│  ┌──────────────────┐         ┌──────────────────┐                       │
│  │ digital_proofs   │<────────┤ content_hashes   │                       │
│  │                  │         │                  │                       │
│  │ - skill_id       │         │ - skill_id       │                       │
│  │ - content_hash   │         │ - hash_value     │                       │
│  │ - platform_sig   │         └──────────────────┘                       │
│  └────────┬─────────┘                                                          │
│           │                                                                  │
│           │    ┌──────────────────────────────────────┐                     │
│           │    │                                      │                     │
│           v    v                                      v                     │
│  ┌──────────────────┐   ┌──────────────┐   ┌──────────────┐             │
│  │   signatures     │   │blockchain_   │   │verification  │             │
│  │                  │   │  records     │   │    _logs     │             │
│  │ - proof_id       │   │              │   │              │             │
│  │ - signer_type    │   │ - proof_id   │   │ - proof_id   │             │
│  │ - signature_val  │   │ - tx_hash    │   │ - skill_id   │             │
│  └──────────────────┘   └──────────────┘   └──────────────┘             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 8.1 为什么商用 Skills 需要数字存证

| 需求 | 传统存储 | 数字签名存证 |
|------|----------|-------------|
| 数据完整性 | 中心化可篡改 | 签名不可伪造 |
| 版权证明 | 需第三方公证 | 双签名即证明 |
| 授权记录 | 可被伪造 | 签名可追溯 |
| 实施成本 | 低 | 低 |
| 维护成本 | 中 | 中 |

## 8.2 存证架构

```
┌─────────────────────────────────────────────────────────────┐
│              商用 Skills 数字存证架构                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  存证数据                                                   │
│  ├── Skill ID (唯一标识)                                   │
│  ├── Content Hash (SHA-256 内容哈希)                       │
│  ├── Author (创作者)                                       │
│  ├── Creation Time (创建时间戳)                            │
│  ├── Platform Signature (平台数字签名)                     │
│  └── Author Signature (作者数字签名)                       │
│                                                             │
│  存储方式                                                   │
│  └── Skills 完整内容存储于 OSS，签名存储于数据库            │
│                                                             │
│  验证流程                                                   │
│  1. 下载 Skills 内容                                       │
│  2. 计算本地 SHA-256 哈希                                  │
│  3. 验证平台签名（使用平台公钥）                            │
│  4. 验证作者签名（使用作者公钥）                            │
│  5. 一致则内容真实未被篡改                                 │
│                                                             │
│  分阶段实施                                                 │
│  ├── MVP: 中心化哈希存储                                   │
│  ├── 商用期: 数字签名存证                                   │
│  └── 企业期: 可选上链（以太坊 Layer 2）                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 8.3 存证数据结构

```json
{
  "skill_id": "skill_com_abc123",
  "content_hash": "sha256:3a7b8c9d1e2f...4b5m6n",
  "author": {
    "id": 12345,
    "username": "ACME_Technologies",
    "public_key": "0xabc123..."
  },
  "name": "Enterprise Payment Gateway Solution",
  "version": "2.1.0",
  "category": "tech",
  "created_at": 1737657600,
  "platform_signature": "0x9f8e7d6c5b4a...3210",
  "author_signature": "0x123456789abc...def0"
}
```

## 8.4 上链策略（分阶段）

| 阶段 | 存证方式 | 原因 |
|-------------|----------|------|
| **MVP 阶段** | 数据库哈希存储 | 验证需求低，成本低 |
| **商用验证期** | 数字签名存证 | 需要版权证明，成本可控 |
| **企业定制期** | 可选上链（以太坊 Layer 2） | 大客户需求，安全性最高 |

## 8.5 为什么暂不使用区块链

| 考虑因素 | 分析 |
|---------|------|
| **成本** | 链上存储成本高，初期不划算 |
| **复杂度** | 增加系统复杂度，维护成本高 |
| **用户需求** | 初期用户对区块链需求不强 |
| **替代方案** | 数字签名可满足大部分存证需求 |

**未来升级路径：**
```
数字签名存证
    ↓ (企业客户需求)
以太坊 Layer 2 (Arbitrum/Optimism)
    ↓ (合规需求)
Hyperledger Fabric (联盟链)
```

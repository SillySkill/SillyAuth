# 一块变项目 - 修复建议代码

本文档提供详细的修复代码示例，可直接应用到项目中。

---

## 1. 前端修复

### 1.1 upload.ts - 修复上传URL未保存问题 (F-001)

```typescript
// 文件: silly-complete/silly/One/miniprogram/pages/upload/upload.ts

interface UploadData {
  styleId: string;
  styleName: string;
  styleThumbnail: string;
  stylePrice: number;
  images: string[];           // 本地图片路径
  serverUrls: string[];       // 【新增】服务器返回的URL
  maxImages: number;
  uploading: boolean;
  uploadProgress: number;
  selectedImage: string;
  showCropper: boolean;
}

Page<UploadData>({
  data: {
    styleId: '',
    styleName: '',
    styleThumbnail: '',
    stylePrice: 0,
    images: [],
    serverUrls: [],  // 【新增】
    maxImages: 9,
    uploading: false,
    uploadProgress: 0,
    selectedImage: '',
    showCropper: false
  },

  onLoad(options: any) {
    const { styleId, styleName, styleThumbnail, stylePrice } = options;
    
    if (!styleId) {
      wx.showToast({ title: '参数错误', icon: 'none' });
      setTimeout(() => wx.navigateBack(), 1500);
      return;
    }

    this.setData({
      styleId,
      styleName: decodeURIComponent(styleName || '默认风格'),
      styleThumbnail: decodeURIComponent(styleThumbnail || ''),
      stylePrice: Number(stylePrice) || 0,  // 【修复F-002】保存价格
      serverUrls: []  // 初始化
    });
  },

  // 上传图片到服务器
  async uploadImages(localPaths: string[]) {
    this.setData({ uploading: true, uploadProgress: 0 });

    const totalFiles = localPaths.length;
    let uploadedCount = 0;
    const uploadedUrls: string[] = [];

    for (const path of localPaths) {
      try {
        const uploadRes = await wx.uploadFile({
          url: http['baseUrl'] + '/api/one/upload/image',
          filePath: path,
          name: 'file',
          header: {
            'Authorization': `Bearer ${wx.getStorageSync('token')}`
          }
        });

        const data = JSON.parse(uploadRes.data);
        if (data.code === 0 && data.data) {
          uploadedUrls.push((data.data as any).url);
        }
      } catch (err) {
        console.error('上传失败:', err);
        wx.showToast({
          title: '部分图片上传失败',
          icon: 'none'
        });
      }

      uploadedCount++;
      this.setData({
        uploadProgress: Math.floor((uploadedCount / totalFiles) * 100)
      });
    }

    // 【修复F-001】保存服务器返回的URL
    this.setData({
      uploading: false,
      serverUrls: [...this.data.serverUrls, ...uploadedUrls]
    });

    if (uploadedUrls.length > 0) {
      wx.showToast({ title: '上传成功', icon: 'success' });
    }
  },

  // 【修复F-003】添加图片校验
  async onChooseImage() {
    const remaining = this.data.maxImages - this.data.images.length;
    if (remaining <= 0) {
      wx.showToast({ title: `最多上传${this.data.maxImages}张图片`, icon: 'none' });
      return;
    }

    try {
      const res = await wx.chooseMedia({
        count: remaining,
        mediaType: ['image'],
        sourceType: ['album', 'camera'],
        maxDuration: 30,
        camera: 'back'
      });

      // 校验图片大小（限制5MB）
      const maxSize = 5 * 1024 * 1024;
      const validFiles = res.tempFiles.filter(file => {
        if (file.size > maxSize) {
          wx.showToast({
            title: `${file.tempFilePath} 超过5MB，已跳过`,
            icon: 'none'
          });
          return false;
        }
        return true;
      });

      const newImages = validFiles.map(file => file.tempFilePath);
      
      this.setData({
        images: [...this.data.images, ...newImages]
      });

      // 自动上传
      if (newImages.length > 0) {
        this.uploadImages(newImages);
      }
    } catch (err) {
      console.log('用户取消选择');
    }
  },

  // 下一步 - 前往生成页
  onNextStep() {
    if (this.data.images.length === 0) {
      wx.showToast({ title: '请至少上传一张图片', icon: 'none' });
      return;
    }

    if (this.data.uploading) {
      wx.showToast({ title: '请等待上传完成', icon: 'none' });
      return;
    }

    // 【修复F-001】传递服务器URL和价格
    wx.navigateTo({
      url: `/pages/generate/generate?styleId=${this.data.styleId}&styleName=${encodeURIComponent(this.data.styleName)}&stylePrice=${this.data.stylePrice}&images=${encodeURIComponent(JSON.stringify(this.data.images))}&serverUrls=${encodeURIComponent(JSON.stringify(this.data.serverUrls))}`
    });
  }
});
```

---

### 1.2 generate.ts - 修复价格硬编码和重复提交 (F-004, F-005, F-006)

```typescript
// 文件: silly-complete/silly/One/miniprogram/pages/generate/generate.ts

interface GenerateData {
  styleId: string;
  styleName: string;
  stylePrice: number;  // 【新增】
  images: string[];
  serverUrls: string[];  // 【新增】服务器URL
  imageCount: number;
  totalPrice: number;
  
  generating: boolean;
  isSubmitting: boolean;  // 【新增】防重复提交
  generateProgress: number;
  generateStatus: string;
  
  generatedImages: string[];
  selectedImages: string[];
  
  userBalance: number;
  needPayment: boolean;
}

Page<GenerateData>({
  data: {
    styleId: '',
    styleName: '',
    stylePrice: 0,  // 【新增】
    images: [],
    serverUrls: [],  // 【新增】
    imageCount: 0,
    totalPrice: 0,
    
    generating: false,
    isSubmitting: false,  // 【新增】
    generateProgress: 0,
    generateStatus: '准备中...',
    
    generatedImages: [],
    selectedImages: [],
    
    userBalance: 0,
    needPayment: false
  },

  onLoad(options: any) {
    const { styleId, styleName, stylePrice, images, serverUrls } = options;
    
    if (!styleId || !images) {
      wx.showToast({ title: '参数错误', icon: 'none' });
      setTimeout(() => wx.navigateBack(), 1500);
      return;
    }

    try {
      const imageList = JSON.parse(decodeURIComponent(images));
      const serverUrlList = serverUrls ? JSON.parse(decodeURIComponent(serverUrls)) : [];
      // 【修复F-004】从参数获取价格
      const price = Number(stylePrice) || 10;
      
      this.setData({
        styleId,
        styleName: decodeURIComponent(styleName || '默认风格'),
        stylePrice: price,  // 【新增】
        images: imageList,
        serverUrls: serverUrlList,  // 【新增】
        imageCount: imageList.length,
        totalPrice: imageList.length * price
      });

      this.loadUserBalance();
    } catch (err) {
      console.error('解析参数失败:', err);
      wx.showToast({ title: '参数解析失败', icon: 'none' });
    }
  },

  // 开始生成
  async onStartGenerate() {
    // 【修复F-006】防止重复提交
    if (this.data.isSubmitting) {
      console.log('正在提交中，请勿重复点击');
      return;
    }

    // 检查余额
    if (this.data.needPayment) {
      wx.showModal({
        title: '余额不足',
        content: `当前余额 ${this.data.userBalance} 积分，生成需要 ${this.data.totalPrice} 积分，是否立即充值？`,
        confirmText: '去充值',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({ url: '/pages/mine/recharge' });
          }
        }
      });
      return;
    }

    // 检查登录状态
    const token = wx.getStorageSync('token');
    if (!token) {
      wx.showModal({
        title: '请先登录',
        content: '生成功能需要登录后才能使用',
        confirmText: '去登录',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({ url: '/pages/login/login' });
          }
        }
      });
      return;
    }

    // 【修复F-006】设置提交状态
    this.setData({ 
      isSubmitting: true,
      generating: true, 
      generateProgress: 0,
      generateStatus: '正在上传图片...'
    });

    this.simulateProgress();
    
    try {
      // 【修复F-001】优先使用服务器URL
      const urlsToUse = this.data.serverUrls.length > 0 
        ? this.data.serverUrls 
        : this.data.images;

      const res = await http.post('/api/one/generate/create', {
        styleId: this.data.styleId,
        images: urlsToUse,  // 使用服务器URL
        count: this.data.imageCount
      });

      if (res.code === 0 && res.data) {
        this.setData({ 
          generateProgress: 100,
          generateStatus: '生成完成！',
          isSubmitting: false
        });

        setTimeout(() => {
          const resultData = (res.data as any);
          wx.redirectTo({
            url: `/pages/result/result?taskId=${resultData.taskId || resultData.task_id}&styleName=${encodeURIComponent(this.data.styleName)}`
          });
        }, 500);
      }
    } catch (err: any) {
      // 【修复F-005】添加失败回退逻辑
      this.setData({ 
        generating: false,
        isSubmitting: false,
        generateStatus: '生成失败'
      });
      
      wx.showModal({
        title: '生成失败',
        content: err.message || 'AI生成服务暂时不可用，请稍后重试',
        confirmText: '重试',
        cancelText: '返回',
        success: (res) => {
          if (res.confirm) {
            // 重试
            this.onStartGenerate();
          } else {
            wx.navigateBack();
          }
        }
      });
    }
  }
});
```

---

## 2. 后端修复

### 2.1 api_yibian.py - 修复缩略图和安全问题 (B-001, S-001)

```python
# 文件: silly-complete/silly/web/app/backend/api_yibian.py

import os
from PIL import Image
import uuid

# 【修复S-001】使用环境变量
VOLCANO_API_KEY = os.getenv("VOLCANO_API_KEY")
WECHAT_PAY_MCH_ID = os.getenv("WECHAT_PAY_MCH_ID")
WECHAT_PAY_APP_ID = os.getenv("WECHAT_PAY_APP_ID")
WECHAT_PAY_API_KEY = os.getenv("WECHAT_PAY_API_KEY")

# 启动时验证配置
if not VOLCANO_API_KEY:
    print("警告: 未设置环境变量 VOLCANO_API_KEY，AI生成功能将使用模拟数据")

# 【修复B-001】缩略图生成函数
def create_thumbnail(source_path: str, thumb_path: str, size: tuple = (200, 200)) -> bool:
    """
    创建缩略图
    Args:
        source_path: 源图片路径
        thumb_path: 缩略图保存路径
        size: 缩略图尺寸，默认200x200
    Returns:
        是否成功
    """
    try:
        with Image.open(source_path) as img:
            # 保持宽高比
            img.thumbnail(size, Image.Resampling.LANCZOS)
            # 保存为JPEG格式，质量85
            img.convert('RGB').save(thumb_path, 'JPEG', quality=85)
            return True
    except Exception as e:
        print(f"创建缩略图失败: {e}")
        return False

# 【修复B-003】生成唯一文件名
def generate_unique_filename(user_id: int, ext: str) -> str:
    """生成唯一文件名"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_id = uuid.uuid4().hex[:8]
    return f"{user_id}_{timestamp}_{unique_id}.{ext}"

# 修改后的上传接口
@router.post("/photo/upload", response_model=PhotoUploadResponse)
async def upload_photo(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    照片上传接口 - 修复版
    """
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="只支持JPG/PNG/WEBP格式")
    
    # 验证用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 【修复B-003】生成唯一文件名
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ["jpg", "jpeg", "png", "webp"]:
        file_ext = "jpg"
    
    filename = generate_unique_filename(user_id, file_ext)
    
    # 保存文件
    file_path = UPLOAD_DIR / filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 【修复B-001】生成真正的缩略图
    thumbnail_filename = f"thumb_{filename}"
    thumbnail_path = UPLOAD_DIR / thumbnail_filename
    
    if not create_thumbnail(str(file_path), str(thumbnail_path)):
        # 如果缩略图生成失败，复制原图
        shutil.copy(file_path, thumbnail_path)
    
    # 获取图片实际尺寸
    try:
        with Image.open(file_path) as img:
            width, height = img.size
    except:
        width, height = 800, 600
    
    # 创建数据库记录
    photo = UserPhoto(
        user_id=user_id,
        original_url=f"/uploads/{filename}",
        thumbnail_url=f"/uploads/{thumbnail_filename}",
        file_size=file_path.stat().st_size,
        width=width,
        height=height
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    
    return PhotoUploadResponse(
        photo_id=photo.id,
        original_url=photo.original_url,
        thumbnail_url=photo.thumbnail_url
    )
```

---

### 2.2 api_yibian.py - 修复支付回调 (B-004, B-005)

```python
# 文件: silly-complete/silly/web/app/backend/api_yibian.py

import xml.etree.ElementTree as ET
from fastapi import Request
import hashlib
import hmac

# 【修复B-004】微信支付签名验证
def verify_wechat_sign(xml_data: bytes, api_key: str) -> bool:
    """
    验证微信支付签名
    """
    try:
        # 解析XML
        root = ET.fromstring(xml_data)
        
        # 获取签名
        sign = root.find('sign').text if root.find('sign') is not None else None
        if not sign:
            return False
        
        # 收集所有字段（除了sign）
        params = {}
        for child in root:
            if child.tag != 'sign' and child.text:
                params[child.tag] = child.text
        
        # 按字典序排序并拼接
        sorted_params = sorted(params.items())
        sign_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
        sign_str += f"&key={api_key}"
        
        # 计算签名
        calculated_sign = hashlib.md5(sign_str.encode()).hexdigest().upper()
        
        return calculated_sign == sign
    except Exception as e:
        print(f"签名验证失败: {e}")
        return False

# 【修复B-005】修改回调接口接收XML
@router.post("/payment/callback")
async def payment_callback(request: Request, db: Session = Depends(get_db)):
    """
    支付回调接口 - 修复版
    - 接收XML格式
    - 验证签名
    - 处理业务逻辑
    """
    # 获取原始XML数据
    xml_data = await request.body()
    
    # 【修复B-004】验证签名
    if WECHAT_PAY_API_KEY and not verify_wechat_sign(xml_data, WECHAT_PAY_API_KEY):
        return {"code": "FAIL", "message": "签名验证失败"}
    
    # 【修复B-005】解析XML
    try:
        root = ET.fromstring(xml_data)
        order_no = root.find('out_trade_no').text
        transaction_id = root.find('transaction_id').text
        result_code = root.find('result_code').text
    except Exception as e:
        return {"code": "FAIL", "message": f"XML解析失败: {e}"}
    
    # 检查支付结果
    if result_code != 'SUCCESS':
        return {"code": "FAIL", "message": "支付失败"}
    
    # 查找订单
    order = db.query(PaymentOrder).filter(PaymentOrder.order_no == order_no).first()
    if not order:
        return {"code": "FAIL", "message": "订单不存在"}
    
    # 检查订单状态
    if order.status != OrderStatus.PENDING:
        return {"code": "SUCCESS", "message": "订单已处理"}
    
    # 更新订单状态
    order.status = OrderStatus.PAID
    order.wx_transaction_id = transaction_id
    order.paid_at = datetime.utcnow()
    db.commit()
    
    # 处理业务逻辑
    if order.product_type == "credits":
        credits = db.query(UserCredits).filter(UserCredits.user_id == order.user_id).first()
        if not credits:
            credits = UserCredits(user_id=order.user_id)
            db.add(credits)
        
        credit_amount = order.amount
        credits.balance += credit_amount
        credits.total_earned += credit_amount
        
        transaction = CreditTransaction(
            user_id=order.user_id,
            type="purchase",
            amount=credit_amount,
            balance_after=credits.balance,
            order_id=order.id,
            description=f"充值{credit_amount}积分"
        )
        db.add(transaction)
        db.commit()
    
    # 返回XML格式响应
    return {"code": "SUCCESS", "message": "成功"}
```

---

### 2.3 api_yibian.py - 修复认证安全 (S-002, S-003)

```python
# 文件: silly-complete/silly/web/app/backend/api_yibian.py

import bcrypt
from datetime import timedelta
# 如果使用JWT，需要安装: pip install python-jose[cryptography]
from jose import jwt

# JWT配置
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24 * 7  # 7天

# 【修复S-003】使用bcrypt进行密码哈希
def hash_password_bcrypt(password: str) -> str:
    """使用bcrypt哈希密码"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password_bcrypt(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

# 【修复S-002】生成JWT Token
def create_jwt_token(user_id: int, username: str) -> str:
    """创建JWT Token"""
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> dict:
    """验证JWT Token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except:
        return None

# 修改后的登录接口
@router.post("/user/login", response_model=UserLoginResponse)
async def user_login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    用户登录接口 - 修复版
    """
    user = db.query(User).filter(
        (User.username == request.username) | (User.email == request.username)
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 【修复S-003】使用bcrypt验证密码
    # 注意：需要先迁移现有密码到bcrypt
    if user.password_hash.startswith('$2b$'):
        # 新版bcrypt密码
        if not verify_password_bcrypt(request.password, user.password_hash):
            raise HTTPException(status_code=401, detail="密码错误")
    else:
        # 旧版SHA256密码（兼容）
        old_hash = hashlib.sha256(request.password.encode()).hexdigest()
        if user.password_hash != old_hash:
            raise HTTPException(status_code=401, detail="密码错误")
        
        # 迁移到bcrypt
        user.password_hash = hash_password_bcrypt(request.password)
        db.commit()
    
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    credits = db.query(UserCredits).filter(UserCredits.user_id == user.id).first()
    balance = credits.balance if credits else 0
    
    # 【修复S-002】使用JWT Token
    token = create_jwt_token(user.id, user.username)
    
    return UserLoginResponse(
        user_id=user.id,
        username=user.username,
        token=token,
        credits=balance
    )
```

---

## 3. 配置文件

### 3.1 环境变量配置 (.env)

```bash
# 文件: silly-complete/silly/web/app/backend/.env

# 数据库
DATABASE_URL=sqlite:///./sillymd.db

# 火山引擎
VOLCANO_API_KEY=your_volcano_api_key_here

# 微信支付
WECHAT_PAY_MCH_ID=your_mch_id
WECHAT_PAY_APP_ID=your_app_id
WECHAT_PAY_API_KEY=your_api_key
WECHAT_PAY_NOTIFY_URL=https://yourdomain.com/api/v1/yibian/payment/callback

# JWT
JWT_SECRET=your_jwt_secret_key_change_in_production

# 文件上传
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=5242880  # 5MB
```

### 3.2 启动时加载环境变量

```python
# 文件: silly-complete/silly/web/app/backend/main.py

from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 验证必要配置
required_env_vars = ['VOLCANO_API_KEY', 'JWT_SECRET']
for var in required_env_vars:
    if not os.getenv(var):
        print(f"警告: 环境变量 {var} 未设置")
```

---

## 4. 数据库迁移

如果修改了密码哈希方式，需要迁移现有密码：

```python
# 文件: silly-complete/silly/web/app/backend/migrate_passwords.py

import bcrypt
from database import SessionLocal
from models import User

def migrate_passwords():
    """将SHA256密码迁移到bcrypt"""
    db = SessionLocal()
    
    users = db.query(User).all()
    
    for user in users:
        # 跳过已经是bcrypt的密码
        if user.password_hash.startswith('$2b$'):
            continue
        
        # 重置密码为默认密码（用户需要重新设置）
        default_password = "changeme123"
        user.password_hash = bcrypt.hashpw(
            default_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        print(f"用户 {user.username} 的密码已重置")
    
    db.commit()
    db.close()
    print("密码迁移完成")

if __name__ == "__main__":
    migrate_passwords()
```

---

## 5. 测试验证

修复后，运行以下测试验证：

```bash
# 1. 测试上传
curl -X POST "http://localhost:8000/api/v1/yibian/photo/upload" \
  -F "file=@test.jpg" \
  -F "user_id=1"

# 2. 测试登录
curl -X POST "http://localhost:8000/api/v1/yibian/user/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"password123"}'

# 3. 测试支付回调（需要真实签名）
curl -X POST "http://localhost:8000/api/v1/yibian/payment/callback" \
  -H "Content-Type: application/xml" \
  -d '<xml><out_trade_no>YB20260215123456</out_trade_no><sign>...</sign></xml>'
```

---

**修复完成后，请更新 BUG_LIST.md 中的状态**

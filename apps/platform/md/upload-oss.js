/**
 * 阿里云 OSS 文件上传脚本
 * 将 hero 目录下的轮播图文件上传到 OSS
 */

const OSS = require('ali-oss');
const path = require('path');
const fs = require('fs');

// OSS 配置
const client = new OSS({
  region: 'cn-shanghai',
  accessKeyId: 'REDACTED_ALIYUN_ACCESS_KEY',
  accessKeySecret: 'REDACTED_ALIYUN_SECRET_KEY',
  bucket: 'jc-st',
  endpoint: 'https://oss-cn-shanghai.aliyuncs.com'
});

// 上传配置
const UPLOAD_CONFIG = {
  localDir: path.join(__dirname, 'hero'),
  remoteDir: 'sillymd/hero',
  files: [
    'lay-1080.mp4',
    'man-1080.mp4',
    'chapter3-features.png'
  ]
};

/**
 * 上传单个文件到 OSS
 */
async function uploadFile(fileName) {
  const localPath = path.join(UPLOAD_CONFIG.localDir, fileName);
  const remotePath = `${UPLOAD_CONFIG.remoteDir}/${fileName}`;

  console.log(`\n📤 开始上传: ${fileName}`);

  // 检查本地文件是否存在
  if (!fs.existsSync(localPath)) {
    console.error(`❌ 文件不存在: ${localPath}`);
    return false;
  }

  try {
    const result = await client.put(remotePath, localPath, {
      headers: {
        'Content-Type': getContentType(fileName),
        'Cache-Control': 'max-age=31536000' // 缓存一年
      }
    });

    console.log(`✅ 上传成功: ${fileName}`);
    console.log(`   访问 URL: https://jc-st.oss-cn-shanghai.aliyuncs.com/${remotePath}`);
    console.log(`   文件大小: ${formatFileSize(fs.statSync(localPath).size)}`);
    console.log(`   ETag: ${result.etag}`);

    return result;
  } catch (error) {
    console.error(`❌ 上传失败: ${fileName}`);
    console.error(`   错误信息: ${error.message}`);
    return false;
  }
}

/**
 * 批量上传文件
 */
async function uploadAll() {
  console.log('='.repeat(60));
  console.log('阿里云 OSS 文件上传工具');
  console.log('='.repeat(60));
  console.log(`Bucket: jc-st`);
  console.log(`Region: cn-shanghai`);
  console.log(`目标目录: ${UPLOAD_CONFIG.remoteDir}`);
  console.log('='.repeat(60));

  const results = [];

  for (const fileName of UPLOAD_CONFIG.files) {
    const result = await uploadFile(fileName);
    results.push({ fileName, result });
  }

  // 输出总结
  console.log('\n' + '='.repeat(60));
  console.log('上传完成总结');
  console.log('='.repeat(60));

  const successCount = results.filter(r => r.result).length;
  const failCount = results.filter(r => !r.result).length;

  console.log(`总计: ${results.length} 个文件`);
  console.log(`成功: ${successCount} 个`);
  console.log(`失败: ${failCount} 个`);

  if (successCount > 0) {
    console.log('\n📋 成功上传的文件 URL:');
    results.filter(r => r.result).forEach(r => {
      const url = `https://jc-st.oss-cn-shanghai.aliyuncs.com/${UPLOAD_CONFIG.remoteDir}/${r.fileName}`;
      console.log(`  - ${url}`);
    });
  }

  console.log('='.repeat(60));

  return successCount === results.length;
}

/**
 * 获取文件的 Content-Type
 */
function getContentType(fileName) {
  const ext = path.extname(fileName).toLowerCase();
  const mimeTypes = {
    '.mp4': 'video/mp4',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.svg': 'image/svg+xml'
  };
  return mimeTypes[ext] || 'application/octet-stream';
}

/**
 * 格式化文件大小
 */
function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 执行上传
uploadAll()
  .then(success => {
    if (success) {
      console.log('\n🎉 所有文件上传成功！');
      process.exit(0);
    } else {
      console.log('\n⚠️  部分文件上传失败，请检查错误信息');
      process.exit(1);
    }
  })
  .catch(error => {
    console.error('\n💥 发生错误:', error);
    process.exit(1);
  });

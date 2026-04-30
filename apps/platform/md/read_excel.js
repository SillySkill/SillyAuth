const XLSX = require('xlsx');
const path = require('path');

const filePath = 'E:/silly/md/assets/2026年中山街道公共法律服务信息指引（最新）.xlsx';
const workbook = XLSX.readFile(filePath);
const sheetName = workbook.SheetNames[0];
const sheet = workbook.Sheets[sheetName];

console.log('Excel表格内容：');
console.log('=' .repeat(60));

// Convert to JSON for easier processing
const data = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '' });

// Print first 30 rows
for (let r = 0; r < Math.min(data.length, 30); r++) {
    const row = data[r].filter(cell => cell !== '');
    if (row.length > 0) {
        console.log(`Row ${r + 1}: ${row.join(' | ')}`);
    }
}

console.log('');
console.log('=' .repeat(60));
console.log('');

// Extract potential community names (2-4 Chinese characters)
const names = new Set();
for (let r = 0; r < data.length; r++) {
    for (let c = 0; c < data[r].length; c++) {
        const val = String(data[r][c]).trim();
        // Match community name pattern (2-4 Chinese chars)
        if (/^[\u4e00-\u9fa5]{2,4}$/.test(val)) {
            // Skip common header words
            if (!['居委会', '服务站', '工作站', '工作站室', '名称'].includes(val)) {
                names.add(val);
            }
        }
    }
}

console.log('潜在居委会名称：');
console.log('');
const nameList = Array.from(names).sort();
nameList.forEach((name, i) => {
    console.log(`  ${i + 1}. ${name}`);
});

console.log('');
console.log(`共找到 ${nameList.length} 个名称`);

// Compare with database
const dbNames = [
    "莱顿", "淡家浜", "黄渡浜", "中山苑", "郭家娄", "茸梅",
    "方西", "白云", "南门", "茸虹", "茸吉", "月厦",
    "星辰园", "檀香", "御上海郡", "东鼎", "郑舍", "花锦",
    "三湘四季", "茸达", "星定", "蓝天东", "蓝天西", "东附件",
    "郭家河", "广富林", "松汇", "北九峰", "南其"
];

console.log('');
console.log('=' .repeat(60));
console.log('对比分析：');
console.log('');

// In Excel but not in DB
const inExcelNotDb = nameList.filter(n => !dbNames.includes(n));
// In DB but not in Excel
const inDbNotExcel = dbNames.filter(n => !nameList.includes(n));

console.log(`Excel中有 ${inExcelNotDb.length} 个名称不在数据库中:`);
inExcelNotDb.forEach(n => console.log(`  - ${n}`));

console.log('');
console.log(`数据库中有 ${inDbNotExcel.length} 个名称不在Excel中:`);
inDbNotExcel.forEach(n => console.log(`  - ${n}`));

console.log('');
console.log('共同名称：');
const common = nameList.filter(n => dbNames.includes(n));
common.forEach(n => console.log(`  - ${n}`));
console.log(`共 ${common.length} 个`);

const { createWorker } = require('tesseract.js');
const path = require('path');
const fs = require('fs');

async function runOCR() {
    const imagePath = path.join(__dirname, 'src/frontend/web/public/assets/zhongshan_new.png');

    console.log('Starting OCR with Chinese support...\n');

    // Use a reliable CDN for the Chinese language data
    const worker = await createWorker('chi_sim', 1, {
        langPath: 'https://cdn.jsdelivr.net/npm/tesseract.js@5/4.0.0/tessdata',
        logger: m => {
            if (m.status) {
                const progress = m.progress ? (m.progress * 100).toFixed(1) + '%' : '';
                console.log(`${m.status} ${progress}`);
            }
        }
    });

    try {
        console.log('\nRecognizing text...\n');
        const { data } = await worker.recognize(imagePath);

        console.log('\n=== RECOGNIZED TEXT ===\n');
        console.log(data.text);

        // Save to file
        const outputPath = path.join(__dirname, 'ocr_result.txt');
        fs.writeFileSync(outputPath, data.text, 'utf8');
        console.log(`\nSaved to ${outputPath}`);

    } catch (error) {
        console.error('OCR Error:', error);
    } finally {
        await worker.terminate();
    }
}

runOCR().catch(console.error);

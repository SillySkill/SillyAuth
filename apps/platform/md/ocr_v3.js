const Tesseract = require('tesseract.js');
const path = require('path');

async function ocrImage() {
    const imagePath = path.join(__dirname, 'src/frontend/web/public/assets/zhongshan_new.png');

    console.log('Starting OCR...');

    // Use worker with specific language
    const worker = await Tesseract.createWorker('chi_sim', 1, {
        logger: m => {
            if (m.status) console.log(m.status, m.progress ? (m.progress * 100).toFixed(1) + '%' : '');
        }
    });

    try {
        const { data: { text, words, lines } } = await worker.recognize(imagePath);

        console.log('\n=== Full Text ===');
        console.log(text);

        console.log('\n=== Lines with positions ===');
        lines.forEach(line => {
            console.log(`"${line.text}" | Y: ${line.bbox.y0}-${line.bbox.y1} | X: ${line.bbox.x0}-${line.bbox.x1}`);
        });

    } catch (error) {
        console.error('OCR Error:', error.message);
    } finally {
        await worker.terminate();
    }
}

ocrImage().catch(console.error);

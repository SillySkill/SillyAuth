const Tesseract = require('tesseract.js');
const path = require('path');
const sharp = require('sharp');

async function preprocessAndOCR() {
    const imagePath = path.join(__dirname, 'src/frontend/web/public/assets/zhongshan_new.png');
    const outputPath = path.join(__dirname, 'src/frontend/web/public/assets/zhongshan_preprocessed.png');

    console.log('Preprocessing image...');

    // Preprocess image: increase contrast, convert to grayscale, resize
    try {
        await sharp(imagePath)
            .grayscale()
            .normalize()
            .resize(1600) // Resize to reasonable width
            .toFile(outputPath);
        console.log('Preprocessed image saved to:', outputPath);
    } catch (err) {
        console.log('Sharp preprocessing failed, using original image');
    }

    console.log('\nStarting OCR with improved settings...');

    // Use worker with specific language and settings
    const worker = await Tesseract.createWorker('chi_sim', 1, {
        logger: m => {
            if (m.status) console.log(m.status, m.progress ? (m.progress * 100).toFixed(1) + '%' : '');
        }
    });

    try {
        // Use preprocessed image if available
        const imgToProcess = require('fs').existsSync(outputPath) ? outputPath : imagePath;

        const { data } = await worker.recognize(imgToProcess, {
            rotate: 0
        });

        console.log('\n=== Recognized Text ===');
        console.log(data.text);

        // Also try to get word-level data
        if (data.words && data.words.length > 0) {
            console.log('\n=== Word-level Results ===');
            data.words.forEach(word => {
                if (word.confidence > 60) { // Only show high confidence words
                    console.log(`"${word.text}" at (${word.bbox.x0}, ${word.bbox.y0}) conf: ${word.confidence.toFixed(1)}%`);
                }
            });
        }

    } catch (error) {
        console.error('OCR Error:', error.message);
    } finally {
        await worker.terminate();
    }
}

preprocessAndOCR().catch(console.error);

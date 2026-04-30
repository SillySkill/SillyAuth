const { createWorker } = require('tesseract.js');
const path = require('path');
const fs = require('fs');

async function runOCR() {
    const imagePath = path.join(__dirname, 'src/frontend/web/public/assets/zhongshan_new.png');

    console.log('Starting OCR with Tesseract.js...\n');

    // Create worker with Chinese language
    const worker = await createWorker('chi_sim');

    console.log('Worker initialized, starting recognition...\n');

    try {
        const { data } = await worker.recognize(imagePath);

        console.log('\n=== RECOGNIZED TEXT ===\n');
        console.log(data.text);

        // Also output word positions
        if (data.words && data.words.length > 0) {
            console.log('\n=== WORDS WITH POSITIONS ===\n');

            // Get image dimensions (1600x2853)
            const width = 1600;
            const height = 2853;

            // Group words by approximate Y position (row)
            const rows = {};
            data.words.forEach(word => {
                const y = Math.round(word.bbox.y0 / height * 100);
                if (!rows[y]) rows[y] = [];
                rows[y].push({
                    text: word.text,
                    x: (word.bbox.x0 / width * 100).toFixed(1),
                    conf: word.confidence.toFixed(0)
                });
            });

            // Sort by Y position and print
            Object.keys(rows).sort((a, b) => parseInt(a) - parseInt(b)).forEach(y => {
                console.log(`Row ${y}%: ${rows[y].map(w => `"${w.text}"(${w.x}%)`).join(' ')}`);
            });
        }

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

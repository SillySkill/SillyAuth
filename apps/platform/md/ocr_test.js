const Tesseract = require('tesseract.js');
const path = require('path');

async function analyzeImage() {
    const imagePath = path.join(__dirname, 'src/frontend/web/public/assets/zhongshan_new.png');

    console.log('Image path:', imagePath);
    console.log('Starting OCR analysis...');

    try {
        // Try with Chinese
        console.log('\nTrying Chinese OCR...');
        const resultZh = await Tesseract.recognize(
            imagePath,
            'chi_sim',
            {
                logger: m => console.log(m.status, m.progress)
            }
        );
        console.log('\n=== OCR Results (Chinese) ===');
        console.log(resultZh.data.text);

        // Get lines with positions
        if (resultZh.data.lines) {
            console.log('\n=== Line Positions (Chinese) ===');
            resultZh.data.lines.forEach(line => {
                console.log(`"${line.text}" at y=${line.bbox.y0}-${line.bbox.y1}`);
            });
        }

    } catch (error) {
        console.error('Chinese OCR Error:', error.message);

        // Fallback to English
        console.log('\n\nTrying English OCR...');
        try {
            const resultEn = await Tesseract.recognize(
                imagePath,
                'eng',
                {
                    logger: m => console.log(m.status, m.progress)
                }
            );
            console.log('\n=== OCR Results (English) ===');
            console.log(resultEn.data.text);

            if (resultEn.data.lines) {
                console.log('\n=== Line Positions (English) ===');
                resultEn.data.lines.forEach(line => {
                    console.log(`"${line.text}" at y=${line.bbox.y0}-${line.bbox.y1}`);
                });
            }
        } catch (enError) {
            console.error('English OCR Error:', enError);
        }
    }
}

analyzeImage();

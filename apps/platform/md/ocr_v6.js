const Tesseract = require('tesseract.js');
const sharp = require('sharp');
const path = require('path');
const fs = require('fs');

async function enhanceAndOCR() {
    const imagePath = path.join(__dirname, 'src/frontend/web/public/assets/zhongshan_new.png');
    const outputDir = path.join(__dirname, 'temp', 'enhanced');

    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    console.log('Enhancing and OCR-ing image regions...\n');

    const metadata = await sharp(imagePath).metadata();
    const width = metadata.width;
    const height = metadata.height;

    // Crop and enhance specific regions
    const regions = [
        { name: 'region_1_10', y: 0, h: height * 0.4, desc: 'Top 40% (markers 1-10 area)' },
        { name: 'region_11_20', y: height * 0.35, h: height * 0.35, desc: 'Middle 35% (markers 11-20 area)' },
        { name: 'region_21_24', y: height * 0.65, h: height * 0.35, desc: 'Bottom 35% (markers 21-24 area)' },
    ];

    const worker = await Tesseract.createWorker('chi_sim', 1, {
        logger: m => console.log(`${m.status || ''} ${m.progress ? (m.progress * 100).toFixed(0) + '%' : ''}`)
    });

    for (const region of regions) {
        console.log(`\n=== ${region.name}: ${region.desc} ===`);

        const cropPath = path.join(outputDir, `${region.name}_crop.png`);
        const enhancedPath = path.join(outputDir, `${region.name}_enhanced.png`);

        // Crop
        await sharp(imagePath)
            .extract({
                left: 0,
                top: Math.floor(region.y),
                width: width,
                height: Math.floor(region.h)
            })
            .toFile(cropPath);

        // Enhance: grayscale, contrast, threshold-like effect
        await sharp(cropPath)
            .grayscale()
            .linear(1.5, -128)  // Increase contrast
            .threshold(200)       // Make text more distinct
            .toFile(enhancedPath);

        console.log(`Processing: ${enhancedPath}`);

        try {
            const { data } = await worker.recognize(enhancedPath);

            // Get words with positions
            if (data.words && data.words.length > 0) {
                const relY = region.y / height;
                const sortedWords = data.words
                    .filter(w => w.confidence > 40)
                    .map(w => ({
                        text: w.text,
                        x: (w.bbox.x0 / width * 100).toFixed(1),
                        y: ((relY * height + w.bbox.y0) / height * 100).toFixed(1),
                        conf: w.confidence.toFixed(0)
                    }))
                    .sort((a, b) => parseFloat(a.y) - parseFloat(b.y));

                console.log('\nRecognized words (sorted by Y position):');
                sortedWords.forEach(w => {
                    console.log(`  [${w.y}%] "${w.text}" (conf: ${w.conf}%)`);
                });
            }

            // Also output raw text for manual review
            console.log('\nRaw text:');
            console.log(data.text.substring(0, 1000));

        } catch (err) {
            console.log(`OCR error: ${err.message}`);
        }
    }

    await worker.terminate();
    console.log('\n\nDone!');
}

enhanceAndOCR().catch(console.error);

const Tesseract = require('tesseract.js');
const sharp = require('sharp');
const path = require('path');
const fs = require('fs');

async function cropAndOCR() {
    const imagePath = path.join(__dirname, 'src/frontend/web/public/assets/zhongshan_new.png');
    const outputDir = path.join(__dirname, 'temp', 'crops');

    // Create output directory
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    console.log('Cropping image into regions...\n');

    // Get image dimensions
    const metadata = await sharp(imagePath).metadata();
    const width = metadata.width;
    const height = metadata.height;

    console.log(`Image size: ${width}x${height}\n`);

    // Define regions to crop (top, middle, bottom areas)
    const regions = [
        { name: 'top_north', y: 0, h: height * 0.2, desc: 'Top North area (N direction)' },
        { name: 'upper_middle', y: height * 0.15, h: height * 0.2, desc: 'Upper Middle area' },
        { name: 'middle', y: height * 0.4, h: height * 0.2, desc: 'Middle area' },
        { name: 'lower_middle', y: height * 0.6, h: height * 0.2, desc: 'Lower Middle area' },
        { name: 'bottom_south', y: height * 0.8, h: height * 0.2, desc: 'Bottom South area' },
    ];

    const worker = await Tesseract.createWorker('chi_sim', 1, {
        logger: m => {
            if (m.status === 'recognizing text') {
                process.stdout.write('.');
            }
        }
    });

    const results = [];

    for (const region of regions) {
        console.log(`\n\n=== ${region.name}: ${region.desc} ===`);

        // Crop region
        const cropPath = path.join(outputDir, `${region.name}.png`);
        await sharp(imagePath)
            .extract({
                left: 0,
                top: Math.floor(region.y),
                width: width,
                height: Math.floor(region.h)
            })
            .toFile(cropPath);

        console.log(`Crop saved: ${cropPath}`);

        try {
            const { data } = await worker.recognize(cropPath);

            // Filter for higher confidence results
            const highConfWords = data.words
                ? data.words.filter(w => w.confidence > 50)
                : [];

            if (highConfWords.length > 0) {
                console.log('\nHigh confidence words:');
                highConfWords.forEach(w => {
                    const relY = (region.y + w.bbox.y0) / height * 100;
                    console.log(`  "${w.text}" at (${(w.bbox.x0/width*100).toFixed(1)}%, ${relY.toFixed(1)}%) conf: ${w.confidence.toFixed(0)}%`);
                });
                results.push({ region: region.name, words: highConfWords, fullText: data.text });
            }

            // Also show full text
            console.log('\nFull recognized text:');
            console.log(data.text.substring(0, 500));

        } catch (err) {
            console.log(`  OCR failed: ${err.message}`);
        }
    }

    await worker.terminate();

    // Summary
    console.log('\n\n=== SUMMARY ===');
    console.log('High confidence recognized terms:');
    results.forEach(r => {
        console.log(`\n${r.region}:`);
        r.words.forEach(w => {
            console.log(`  "${w.text}"`);
        });
    });
}

cropAndOCR().catch(console.error);

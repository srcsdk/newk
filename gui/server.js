const express = require('express');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const app = express();
const port = process.argv.includes('--port')
    ? parseInt(process.argv[process.argv.indexOf('--port') + 1])
    : 3000;

const feeds_file = path.join(__dirname, '..', 'feeds.txt');
const research_file = path.join(__dirname, '..', 'research_feeds.txt');

function load_feeds(filepath) {
    if (!fs.existsSync(filepath)) return [];
    return fs.readFileSync(filepath, 'utf8')
        .split('\n')
        .map(l => l.trim())
        .filter(l => l && !l.startsWith('#'));
}

app.get('/api/feeds', (req, res) => {
    const feeds = load_feeds(feeds_file);
    const research = load_feeds(research_file);
    res.json({
        feeds: feeds,
        research: research,
        total: feeds.length + research.length,
    });
});

app.get('/api/scrape', (req, res) => {
    try {
        const scraper = path.join(__dirname, '..', 'scrape.py');
        const output = execSync(
            `python3 ${scraper} --json --limit 20`,
            { timeout: 60000, encoding: 'utf8' }
        );
        res.json(JSON.parse(output));
    } catch (err) {
        res.status(500).json({ error: 'scrape failed', detail: err.message });
    }
});

app.get('/', (req, res) => {
    res.send(`
        <html>
        <head><title>newk</title></head>
        <body style="background:#1e1e1e;color:#ccc;font-family:monospace;padding:20px">
            <h1>newk feed reader</h1>
            <p>endpoints:</p>
            <ul>
                <li><a href="/api/feeds" style="color:#4ec9b0">/api/feeds</a> - list all feeds</li>
                <li><a href="/api/scrape" style="color:#4ec9b0">/api/scrape</a> - scrape recent items</li>
            </ul>
        </body>
        </html>
    `);
});

app.listen(port, () => {
    console.log(`newk server running on http://localhost:${port}`);
});

const categories_file = path.join(__dirname, '..', 'categories.json');

function load_categories() {
    if (!fs.existsSync(categories_file)) return {};
    try {
        return JSON.parse(fs.readFileSync(categories_file, 'utf8'));
    } catch (e) {
        return {};
    }
}

app.get('/api/categories', (req, res) => {
    const cats = load_categories();
    const summary = {};
    for (const [name, data] of Object.entries(cats)) {
        const subcats = data.subcategories || {};
        let feed_count = 0;
        for (const urls of Object.values(subcats)) {
            feed_count += urls.length;
        }
        summary[name] = {
            subcategories: Object.keys(subcats),
            feed_count: feed_count,
        };
    }
    res.json(summary);
});

app.get('/api/category/:name', (req, res) => {
    const cats = load_categories();
    const cat = cats[req.params.name];
    if (!cat) {
        return res.status(404).json({ error: 'category not found' });
    }
    res.json(cat);
});

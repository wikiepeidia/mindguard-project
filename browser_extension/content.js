// Content script to detect phone numbers or links (Simplified demo)
console.log("MindGuard Extension Active");

// Example: Highlight suspicious links (This is just a placeholder for logic)
const links = document.getElementsByTagName('a');
for (let link of links) {
    if (link.href.includes('bit.ly') || link.href.includes('tinyurl')) {
        link.style.border = '2px solid red';
        link.title = 'MindGuard: Link rút gọn có thể nguy hiểm';
    }
}

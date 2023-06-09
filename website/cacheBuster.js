const fs = require('fs');
const hashFiles = require('hash-files');
const path = require('node:path');
const replace = require('replace-in-file');

// to facilitate cache busting:
// - rename built js and css files with a short hash
// - find-and-replace the names in all html

// files we want to rename
const filesToHash = [
    'build/css/style.min.css',
    'build/js/bundle.js',
];

// html files that may need string replacements
const filesToPatch = 'build/**/*.html';

// replacements to make
const replacements = {};

filesToHash.forEach(async (file) => {
    const hash = hashFiles.sync({ files: [file] });
    const fileName = path.parse(file).base;
    const shortHash = hash.substring(0, 6);

    // e.g. /path/example.css becomes /path/example.789abc.css
    const newFile = file.replace(/^(.*)\.(.*)$/, `$1.${shortHash}.$2`);
    const newFileName = path.parse(newFile).base;

    // copy rather than rename in place
    fs.copyFile(file, newFile, (error) => {
        if (error) {
            console.error(error);
        }
    });

    // track string replacement
    replacements[fileName] = newFileName;
});

// find and replace the filenames throughout all passed html files
// this doesn't take context into account, so beware unintended changes
(async function () {
    try {
        const results = await replace({
            files: filesToPatch,
            from: Object.keys(replacements),
            to: Object.values(replacements),
        });
        console.log('cache buster replacing:', replacements);
        changedResults = results.filter((result) => result.hasChanged);
        console.log(`cache buster renamed ${changedResults.length} files`);
    } catch (error) {
        console.error('cache buster error replacing files:', error);
    }
})();

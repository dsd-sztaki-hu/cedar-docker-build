import { useState, useEffect } from 'react';
import 'json-diff-kit/dist/viewer.css';
import { Differ, Viewer } from 'json-diff-kit';

function App() {
    const [message, setMessage] = useState({before: {}, after: {}});

    useEffect(() => {
        const handleReceiveMessage = (event) => {
            // Validate the origin if it's important for security
            // if (event.origin !== "http://localhost:4200") {
            //     console.log('Origin not recognized:', event.origin);
            //     return;
            // }
            setMessage(event.data);
        };

        window.addEventListener('message', handleReceiveMessage);

        return () => {
            window.removeEventListener('message', handleReceiveMessage);
        };
    }, []);

    const differ = new Differ({
        detectCircular: true,
        maxDepth: undefined,
        showModifications: true,
        arrayDiffMethod: 'lcs',
        ignoreCase: false,
        recursiveEqual: true
    });
    const diff = differ.diff(message.before, message.after);

    const viewerProps = {
        diff: diff, // Pass the calculated diff
        indent: 4,
        lineNumbers: true,
        highlightInlineDiff: true,
        inlineDiffOptions: {
            mode: 'word',
            wordSeparator: ' '
        },
        hideUnchangedLines: true,
        virtual: false
    };

    return (
        <div className="App">
            <header className="App-header">
                <Viewer
                    {...viewerProps}
                />
            </header>
        </div>

    );
}

export default App;

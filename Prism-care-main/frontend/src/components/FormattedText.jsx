// Renders AI responses that use light markdown: **bold** and "- " bullets.
export default function FormattedText({ text = '', className = '' }) {
    const lines = String(text).split('\n');

    const renderInline = (line, key) =>
        line.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
            part.startsWith('**') && part.endsWith('**') && part.length > 4
                ? <strong key={`${key}-${i}`}>{part.slice(2, -2)}</strong>
                : <span key={`${key}-${i}`}>{part}</span>
        );

    return (
        <div className={className}>
            {lines.map((line, idx) => {
                const bullet = line.match(/^\s*[-*•]\s+(.*)$/);
                if (bullet) {
                    return (
                        <div key={idx} className="flex gap-2 pl-1">
                            <span aria-hidden="true">•</span>
                            <span>{renderInline(bullet[1], idx)}</span>
                        </div>
                    );
                }
                return line.trim() === ''
                    ? <div key={idx} className="h-2" />
                    : <div key={idx}>{renderInline(line, idx)}</div>;
            })}
        </div>
    );
}

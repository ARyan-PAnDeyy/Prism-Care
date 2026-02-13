export default function Card({
    children,
    variant = 'default',
    className = '',
    ...props
}) {
    const variants = {
        default: 'bg-white shadow-md hover:shadow-lg',
        gradient: 'bg-gradient-to-br from-primary to-secondary text-white shadow-lg',
        glass: 'bg-white/70 backdrop-blur-md shadow-lg border border-white/20',
        outlined: 'bg-transparent border-2 border-slate-200 hover:border-primary',
        interactive: 'bg-white shadow-md hover:shadow-xl hover:-translate-y-1 cursor-pointer',
    };

    return (
        <div
            className={`rounded-softer p-6 transition-all duration-200 ${variants[variant]} ${className}`}
            {...props}
        >
            {children}
        </div>
    );
}

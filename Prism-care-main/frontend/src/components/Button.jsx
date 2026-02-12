import { Loader2 } from 'lucide-react';

export default function Button({
    children,
    variant = 'primary',
    size = 'md',
    loading = false,
    disabled = false,
    className = '',
    ...props
}) {
    const baseStyles = 'font-medium rounded-soft transition-all duration-200 inline-flex items-center justify-center';

    const variants = {
        primary: 'bg-primary hover:bg-primary-600 text-white shadow-md hover:shadow-lg disabled:bg-slate-300',
        secondary: 'bg-secondary hover:bg-secondary-600 text-white shadow-md hover:shadow-lg disabled:bg-slate-300',
        outline: 'border-2 border-primary text-primary hover:bg-primary hover:text-white disabled:border-slate-300 disabled:text-slate-300',
        ghost: 'text-primary hover:bg-primary/10 disabled:text-slate-300',
        danger: 'bg-danger hover:bg-danger-600 text-white shadow-md hover:shadow-lg disabled:bg-slate-300',
    };

    const sizes = {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg',
    };

    return (
        <button
            className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className} ${(disabled || loading) ? 'cursor-not-allowed opacity-60' : ''
                }`}
            disabled={disabled || loading}
            {...props}
        >
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {children}
        </button>
    );
}

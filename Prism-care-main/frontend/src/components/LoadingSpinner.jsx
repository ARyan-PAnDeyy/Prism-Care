import { Loader2 } from 'lucide-react';

export default function LoadingSpinner({ variant = 'spinner', size = 'md' }) {
    const sizes = {
        sm: 'h-4 w-4',
        md: 'h-8 w-8',
        lg: 'h-12 w-12',
    };

    if (variant === 'spinner') {
        return (
            <div className="flex justify-center items-center">
                <Loader2 className={`${sizes[size]} animate-spin text-primary`} />
            </div>
        );
    }

    if (variant === 'dots') {
        return (
            <div className="flex space-x-2 justify-center items-center">
                <div className="h-3 w-3 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="h-3 w-3 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="h-3 w-3 bg-primary rounded-full animate-bounce"></div>
            </div>
        );
    }

    if (variant === 'pulse') {
        return (
            <div className="flex justify-center items-center">
                <div className={`${sizes[size]} bg-primary rounded-full animate-pulse`}></div>
            </div>
        );
    }

    return null;
}

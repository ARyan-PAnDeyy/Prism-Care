import { X } from 'lucide-react';
import { useEffect } from 'react';

export default function Modal({ isOpen, onClose, children, closeOnOutsideClick = true }) {
    useEffect(() => {
        const handleEscape = (e) => {
            if (e.key === 'Escape' && isOpen) {
                onClose();
            }
        };

        document.addEventListener('keydown', handleEscape);
        return () => document.removeEventListener('keydown', handleEscape);
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/50 backdrop-blur-sm"
                onClick={closeOnOutsideClick ? onClose : undefined}
            />

            {/* Modal Content */}
            <div className="relative bg-white rounded-softer shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto animate-in fade-in zoom-in duration-200">
                {/* Close Button */}
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 p-2 rounded-lg hover:bg-slate-100 transition-colors"
                >
                    <X className="h-5 w-5" />
                </button>

                {children}
            </div>
        </div>
    );
}

Modal.Header = function ModalHeader({ children }) {
    return (
        <div className="px-6 pt-6 pb-4 border-b">
            <h2 className="text-2xl font-bold text-slate-900">{children}</h2>
        </div>
    );
};

Modal.Body = function ModalBody({ children }) {
    return <div className="px-6 py-4">{children}</div>;
};

Modal.Footer = function ModalFooter({ children }) {
    return (
        <div className="px-6 py-4 border-t bg-slate-50 flex justify-end space-x-3 rounded-b-softer">
            {children}
        </div>
    );
};

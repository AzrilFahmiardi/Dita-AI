import { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { XMarkIcon, ClipboardDocumentIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

/**
 * Modal to display audit log details
 * Shows formatted JSON data with copy to clipboard functionality
 */
const LogDetailsModal = ({ isOpen, onClose, log }) => {
  const handleCopyToClipboard = () => {
    const jsonString = JSON.stringify(log, null, 2);
    navigator.clipboard.writeText(jsonString)
      .then(() => {
        toast.success('Log details copied to clipboard');
      })
      .catch(() => {
        toast.error('Failed to copy to clipboard');
      });
  };

  if (!log) return null;

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-3xl transform overflow-hidden rounded-lg bg-white shadow-xl transition-all">
                <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
                  <Dialog.Title className="text-lg font-semibold text-slate-900">
                    Audit Log Details
                  </Dialog.Title>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={handleCopyToClipboard}
                      className="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 transition-colors"
                    >
                      <ClipboardDocumentIcon className="h-4 w-4" />
                      <span>Copy JSON</span>
                    </button>
                    <button
                      onClick={onClose}
                      className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors"
                    >
                      <XMarkIcon className="h-5 w-5" />
                    </button>
                  </div>
                </div>

                <div className="px-6 py-4">
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm font-medium text-slate-500">Timestamp</p>
                      <p className="text-sm text-slate-900 mt-1">
                        {new Date(log.timestamp).toLocaleString('id-ID', {
                          dateStyle: 'medium',
                          timeStyle: 'medium'
                        })}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-500">User</p>
                      <p className="text-sm text-slate-900 mt-1">
                        {log.details?.username || log.user?.username || log.username || 'System'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-500">Action</p>
                      <p className="text-sm text-slate-900 mt-1">{log.action}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-500">Resource</p>
                      <p className="text-sm text-slate-900 mt-1">{log.resource}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-500">Status</p>
                      <p className="text-sm text-slate-900 mt-1">
                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                          (log.details?.status || 'success') === 'success' 
                            ? 'bg-emerald-100 text-emerald-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {log.details?.status || 'success'}
                        </span>
                      </p>
                    </div>
                    {log.resource_id && (
                      <div>
                        <p className="text-sm font-medium text-slate-500">Resource ID</p>
                        <p className="text-sm text-slate-900 mt-1">{log.resource_id}</p>
                      </div>
                    )}
                  </div>

                  <div>
                    <p className="text-sm font-medium text-slate-500 mb-2">Full Details (JSON)</p>
                    <div className="rounded-lg bg-slate-50 border border-slate-200 p-4 overflow-auto max-h-96">
                      <pre className="text-xs text-slate-700 font-mono whitespace-pre-wrap">
                        {JSON.stringify(log, null, 2)}
                      </pre>
                    </div>
                  </div>
                </div>

                <div className="flex justify-end gap-3 border-t border-slate-200 px-6 py-4">
                  <button
                    onClick={onClose}
                    className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
                  >
                    Close
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};

export default LogDetailsModal;

import { useState, useEffect } from 'react';
import { Bars3Icon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import Sidebar from '../components/layout/Sidebar';
import Badge from '../components/common/Badge';
import { useVoiceChat } from '../hooks/useVoiceChat';
import { VoiceOrb } from '../components/VoiceOrb';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * Voice Assistant page - Landing page after login
 */
const VoiceAssistantPage = () => {
  const { user } = useAuth();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const { connectionStatus, ditaState, transcript, response } = useVoiceChat();
  const [showFullscreenResponse, setShowFullscreenResponse] = useState(false);

  useEffect(() => {
    if (response && (ditaState === 'speaking' || ditaState === 'idle')) {
      setShowFullscreenResponse(true);
    } else {
      setShowFullscreenResponse(false);
    }
  }, [response, ditaState]);

  const getStateLabel = (state) => {
    const labels = {
      idle: 'Standby',
      listening: 'Mendengarkan wake word...',
      wake_word_detected: 'Wake word terdeteksi!',
      recording: 'Merekam suara...',
      processing: 'Memproses...',
      speaking: 'Berbicara...',
      paused: 'Menunggu login...',
    };
    return labels[state] || state;
  };

  const getConnectionColor = (status) => {
    const colors = {
      connected: 'text-green-400',
      connecting: 'text-yellow-400',
      disconnected: 'text-red-400',
      error: 'text-red-500',
    };
    return colors[status] || 'text-gray-400';
  };

  if (showFullscreenResponse) {
    return (
      <div className="relative min-h-screen bg-white">
        <div className="fixed top-0 left-0 right-0 z-40 bg-white border-b border-slate-200">
          <div className="flex items-center justify-between px-6 py-4">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <Bars3Icon className="h-6 w-6 text-slate-700" />
            </button>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${ditaState === 'speaking' ? 'bg-blue-500 animate-pulse' : 'bg-green-500'}`} />
              <span className="text-sm font-medium text-slate-600">
                {ditaState === 'speaking' ? 'Sedang menjawab' : 'Siap'}
              </span>
            </div>
          </div>
        </div>

        <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

        <div className="pt-20 px-8 md:px-16 lg:px-24 xl:px-32 pb-16 min-h-screen flex items-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full max-w-6xl mx-auto"
          >
            <div className="mb-8">
              <h2 className="text-2xl font-semibold text-slate-800">
                Jawaban DITA
              </h2>
              <div className="mt-2 h-1 w-20 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"></div>
            </div>

            <div className="prose prose-lg max-w-none">
              <p className="text-slate-700 text-2xl md:text-3xl leading-relaxed font-normal whitespace-pre-wrap">
                {response}
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-white">
      <div className="fixed top-0 left-0 right-0 z-40 bg-white border-b border-slate-200">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <Bars3Icon className="h-6 w-6 text-slate-700" />
            </button>
            <h2 className="text-xl font-semibold text-slate-900">
              DITA Voice Assistant
            </h2>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${connectionStatus === 'connected' ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm text-slate-600">
                {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
              </span>
            </div>

            {/* User info */}
            <div className="hidden sm:flex items-center gap-3 pl-4 border-l border-slate-200">
              <div className="text-right">
                <p className="text-sm font-medium text-slate-900">
                  {user?.full_name}
                </p>
              </div>
              <Badge role={user?.role?.name} variant="role" />
            </div>
          </div>
        </div>
      </div>

      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

      {/* Main content  */}
      <div className="pt-20 min-h-screen bg-gradient-to-b from-white to-slate-50 flex items-center justify-center p-8">
        <div className="max-w-4xl w-full space-y-12">
          <div className="text-center">
            <motion.h1
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-4xl font-bold text-slate-900 mb-3"
            >
              DITA AI Assistant
            </motion.h1>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="text-slate-600"
            >
              Katakan "Hey Dita" untuk memulai percakapan
            </motion.p>
          </div>

          {/* Voice Orb */}
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="flex justify-center"
          >
            <VoiceOrb state={ditaState} />
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-center"
          >
            <div className="inline-flex items-center gap-2 px-6 py-3 bg-white border border-slate-200 rounded-lg shadow-sm">
              <div className={`w-2 h-2 rounded-full ${
                ditaState === 'listening' ? 'bg-blue-500 animate-pulse' :
                ditaState === 'recording' ? 'bg-blue-600' :
                ditaState === 'processing' ? 'bg-blue-600 animate-pulse' :
                ditaState === 'speaking' ? 'bg-blue-500' :
                'bg-slate-400'
              }`} />
              <span className="text-lg font-medium text-slate-700">
                {getStateLabel(ditaState)}
              </span>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default VoiceAssistantPage;


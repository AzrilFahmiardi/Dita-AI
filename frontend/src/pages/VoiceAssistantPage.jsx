import { useState } from 'react';
import { Bars3Icon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import Sidebar from '../components/layout/Sidebar';
import Badge from '../components/common/Badge';
import { useVoiceChat } from '../hooks/useVoiceChat';
import { VoiceOrb } from '../components/VoiceOrb';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * Voice Assistant page - Landing page after login
 * Wraps the existing Dita voice interface with authentication
 */
const VoiceAssistantPage = () => {
  const { user } = useAuth();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const { connectionStatus, ditaState, transcript, response } = useVoiceChat();

  const getStateLabel = (state) => {
    const labels = {
      idle: 'Standby',
      listening: 'Mendengarkan wake word...',
      wake_word_detected: 'Wake word terdeteksi!',
      recording: 'Merekam suara...',
      processing: 'Memproses...',
      speaking: 'Berbicara...',
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

  return (
    <div className="relative min-h-screen">
      <div className="fixed top-0 left-0 right-0 z-40 bg-white border-b border-slate-200">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <Bars3Icon className="h-6 w-6 text-slate-700" />
            </button>
            <h2 className="text-lg font-semibold text-slate-900">
              DITA Voice Assistant
            </h2>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-3">
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

      <div className="pt-16 min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-8">
        <div className="max-w-4xl w-full space-y-8">
          <div className="text-center">
            <motion.h1
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-5xl font-bold text-white mb-2"
            >
              Dita AI Assistant
            </motion.h1>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="flex items-center justify-center gap-2"
            >
              <div className={`w-2 h-2 rounded-full ${connectionStatus === 'connected' ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
              <span className={`text-sm ${getConnectionColor(connectionStatus)}`}>
                {connectionStatus === 'connected' ? 'Dashboard Connected' : 'Dashboard Disconnected'}
              </span>
            </motion.div>
          </div>

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
            <p className="text-2xl font-medium text-purple-300">
              {getStateLabel(ditaState)}
            </p>
          </motion.div>

          <AnimatePresence mode="wait">
            {transcript && (
              <motion.div
                key="transcript"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-purple-500/30"
              >
                <h3 className="text-sm font-semibold text-purple-400 mb-2">Anda berkata:</h3>
                <p className="text-lg text-white">{transcript}</p>
              </motion.div>
            )}
          </AnimatePresence>

          <AnimatePresence mode="wait">
            {response && (
              <motion.div
                key="response"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-blue-500/30"
              >
                <h3 className="text-sm font-semibold text-blue-400 mb-2">Dita menjawab:</h3>
                <p className="text-lg text-white leading-relaxed">{response}</p>
              </motion.div>
            )}
          </AnimatePresence>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-center text-sm text-gray-400"
          >
            <p>Katakan "Hey Dita" untuk memulai percakapan</p>
            <p className="mt-1 text-xs">Authenticated as: {user?.full_name || user?.username}</p>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default VoiceAssistantPage;


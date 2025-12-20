import { motion } from 'framer-motion';

export const VoiceOrb = ({ state }) => {
  const getOrbColor = () => {
    const colors = {
      idle: 'from-slate-400 to-slate-500',           
      listening: 'from-blue-400 to-blue-600',       
      wake_word_detected: 'from-blue-500 to-blue-700', 
      recording: 'from-blue-500 to-blue-700',       
      processing: 'from-blue-600 to-blue-800',       
      speaking: 'from-blue-500 to-blue-700',        
      paused: 'from-slate-300 to-slate-400',        
    };
    return colors[state] || colors.idle;
  };

  const getAnimationScale = () => {
    if (state === 'idle') return [1, 1.05, 1];
    if (state === 'listening') return [1, 1.1, 1];
    if (state === 'wake_word_detected') return [1, 1.3, 1];
    if (state === 'recording') return [1, 1.15, 1];
    if (state === 'processing') return [1, 1.2, 1, 1.2, 1];
    if (state === 'speaking') return [1, 1.25, 1];
    return [1];
  };

  const getAnimationDuration = () => {
    if (state === 'idle') return 3;
    if (state === 'listening') return 2;
    if (state === 'wake_word_detected') return 0.5;
    if (state === 'recording') return 1.5;
    if (state === 'processing') return 2;
    if (state === 'speaking') return 1;
    return 3;
  };

  return (
    <div className="relative w-64 h-64 flex items-center justify-center">
      {state !== 'idle' && state !== 'paused' && (
        <>
          <motion.div
            className="absolute inset-0 rounded-full blur-xl"
            animate={{
              scale: getAnimationScale(),
              opacity: [0.3, 0.6, 0.3],
            }}
            transition={{
              duration: getAnimationDuration(),
              repeat: Infinity,
              ease: "easeInOut",
            }}
            style={{
              background: `radial-gradient(circle, rgba(59, 130, 246, 0.4) 0%, rgba(59, 130, 246, 0) 70%)`,
            }}
          />

          <motion.div
            className="absolute inset-0 rounded-full blur-2xl"
            animate={{
              scale: getAnimationScale().map(s => s + 0.1),
              opacity: [0.2, 0.4, 0.2],
            }}
            transition={{
              duration: getAnimationDuration() + 0.5,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 0.2,
            }}
            style={{
              background: `radial-gradient(circle, rgba(37, 99, 235, 0.3) 0%, rgba(37, 99, 235, 0) 70%)`,
            }}
          />
        </>
      )}

      {/* Main orb */}
      <motion.div
        className={`relative w-48 h-48 rounded-full bg-gradient-to-br ${getOrbColor()} shadow-2xl`}
        animate={{
          scale: getAnimationScale(),
        }}
        transition={{
          duration: getAnimationDuration(),
          repeat: Infinity,
          ease: "easeInOut",
        }}
      >
        <div className="absolute inset-4 rounded-full bg-white/20 blur-md" />
        
        <div className="absolute top-8 left-8 w-16 h-16 rounded-full bg-white/40 blur-xl" />

        {state === 'speaking' && (
          <>
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-white/30"
              animate={{
                scale: [1, 1.5],
                opacity: [0.6, 0],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: "easeOut",
              }}
            />
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-white/30"
              animate={{
                scale: [1, 1.5],
                opacity: [0.6, 0],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: "easeOut",
                delay: 0.3,
              }}
            />
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-white/30"
              animate={{
                scale: [1, 1.5],
                opacity: [0.6, 0],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: "easeOut",
                delay: 0.6,
              }}
            />
          </>
        )}

        {state === 'recording' && (
          <motion.div
            className="absolute inset-0 rounded-full bg-white/20"
            animate={{
              opacity: [0, 0.5, 0],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        )}
      </motion.div>
    </div>
  );
};

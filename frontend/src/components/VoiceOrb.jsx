import { motion } from 'framer-motion';

export const VoiceOrb = ({ state }) => {
  const getOrbColor = () => {
    const colors = {
      idle: 'from-indigo-400 to-purple-500',
      listening: 'from-green-400 to-green-600',
      wake_word_detected: 'from-yellow-400 to-orange-500',
      recording: 'from-blue-400 to-blue-600',
      processing: 'from-purple-400 to-pink-500',
      speaking: 'from-purple-500 to-purple-700',
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
      {/* Outer glow rings */}
      {state !== 'idle' && (
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
              background: `radial-gradient(circle, rgba(168, 85, 247, 0.4) 0%, rgba(168, 85, 247, 0) 70%)`,
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
              background: `radial-gradient(circle, rgba(147, 51, 234, 0.3) 0%, rgba(147, 51, 234, 0) 70%)`,
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
        {/* Inner glow */}
        <div className="absolute inset-4 rounded-full bg-white/20 blur-md" />
        
        {/* Highlight */}
        <div className="absolute top-8 left-8 w-16 h-16 rounded-full bg-white/40 blur-xl" />

        {/* Wave circles for speaking state */}
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

        {/* Recording pulse */}
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

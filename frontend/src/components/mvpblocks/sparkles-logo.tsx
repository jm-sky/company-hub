'use client'

import { SparklesCore } from '@/components/ui/sparkles'

export default function SparklesLogo() {
  return (
    <div className="w-full bg-black flex flex-col items-center justify-center overflow-hidden">
      <h1 className="mt-20 text-5xl md:text-7xl lg:text-9xl font-bold text-center text-white relative z-20">
        <span className="bg-gradient-to-b from-white to-gray-300 bg-clip-text text-transparent">Company</span>
        <span className="bg-gradient-to-r from-sky-400 via-blue-500 to-sky-400 bg-clip-text text-transparent">Hub</span>
      </h1>
      <div className="w-full md:w-1/2 h-40 relative">
        {/* Gradients */}
        <div className="absolute inset-x-10 md:inset-x-20 top-0 bg-gradient-to-r from-transparent via-indigo-500 to-transparent h-[3px] w-3/4 blur-sm" />
        <div className="absolute inset-x-10 md:inset-x-20 top-0 bg-gradient-to-r from-transparent via-indigo-500 to-transparent h-[2px] w-3/4" />
        <div className="absolute inset-x-30 md:inset-x-60 top-0 bg-gradient-to-r from-transparent via-sky-500 to-transparent h-[8px] w-1/4 blur-sm" />
        <div className="absolute inset-x-30 md:inset-x-60 top-0 bg-gradient-to-r from-transparent via-sky-500 to-transparent h-[2px] w-1/4" />

        {/* Core component */}
        <SparklesCore
          background="transparent"
          minSize={0.4}
          maxSize={1.5}
          particleDensity={1200}
          className="w-full h-full"
          particleColor="#FFFFFF"
        />

        {/* Radial Gradient to prevent sharp edges */}
        <div className="absolute inset-0 w-full h-full bg-black [mask-image:radial-gradient(350px_200px_at_top,transparent_20%,white)]"></div>
      </div>
    </div>
  )
}

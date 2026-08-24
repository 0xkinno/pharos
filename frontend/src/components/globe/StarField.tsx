'use client'

import { useEffect, useRef } from 'react'

interface StarFieldProps {
  starCount?: number
}

export default function StarField({ starCount = 200 }: StarFieldProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
      drawStars()
    }

    interface Star {
      x: number
      y: number
      radius: number
      opacity: number
      twinkleSpeed: number
      phase: number
    }

    const stars: Star[] = Array.from({ length: starCount }, () => ({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      radius: Math.random() * 1.2 + 0.2,
      opacity: Math.random() * 0.7 + 0.1,
      twinkleSpeed: Math.random() * 0.02 + 0.005,
      phase: Math.random() * Math.PI * 2,
    }))

    let animFrame: number
    let time = 0

    function drawStars() {
      if (!ctx || !canvas) return
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      for (const star of stars) {
        const twinkle = Math.sin(time * star.twinkleSpeed + star.phase) * 0.3
        const alpha = Math.max(0, Math.min(1, star.opacity + twinkle))

        ctx.beginPath()
        ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(232, 232, 237, ${alpha})`
        ctx.fill()
      }
    }

    function animate() {
      time++
      drawStars()
      animFrame = requestAnimationFrame(animate)
    }

    window.addEventListener('resize', resize)
    resize()
    animate()

    return () => {
      window.removeEventListener('resize', resize)
      cancelAnimationFrame(animFrame)
    }
  }, [starCount])

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        inset: 0,
        pointerEvents: 'none',
        zIndex: 0,
        opacity: 0.6,
      }}
    />
  )
}

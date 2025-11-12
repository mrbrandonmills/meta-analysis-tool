# Sound Effects Guide - Highlight Demo

## Overview

This guide details where and when sound effects should be triggered in the Highlight Demo for maximum cinematic impact. All sound cues are marked in the component code with `data-sound-effect` attributes.

---

## Sound Effect Map

### 1. Dramatic Intro (Stage: Intro)
**Trigger Point**: When intro stage begins
**Duration**: 2 seconds
**Audio Description**: Deep orchestral hit with low rumble
**Similar to**: ESPN "DUN DUN" intro sound
**Example**: [BBC Orchestral Hit](https://freesound.org/people/beskhu/sounds/456351/)

```typescript
soundEffect: 'dramatic-intro'
```

**Suggested Audio Characteristics**:
- Frequency: 80-200 Hz (low end)
- Impact: High
- Reverb: Large hall
- Volume: -3 dB

---

### 2. Project Start (Stage: Create)
**Trigger Point**: When project creation begins
**Duration**: 1 second
**Audio Description**: Rocket launch whoosh with rising pitch
**Similar to**: Spacecraft taking off
**Example**: [Rocket Whoosh](https://freesound.org/people/InspectorJ/sounds/394231/)

```typescript
soundEffect: 'project-start'
```

**Suggested Audio Characteristics**:
- Start frequency: 200 Hz → End: 2000 Hz
- Whoosh with doppler effect
- Quick attack, medium decay
- Volume: -6 dB

---

### 3. Search Whoosh (Stage: Search)
**Trigger Point**: When database search begins
**Duration**: 0.5 seconds (repeating)
**Audio Description**: Fast scanner beep sequence
**Similar to**: Radar ping or sonar pulse
**Example**: [Scanner Beep](https://freesound.org/people/ProjectsU012/sounds/341695/)

```typescript
soundEffect: 'search-whoosh'
```

**Suggested Audio Characteristics**:
- Pattern: Beep... beep.. beep. beepbeepbeep
- Frequency: 800-1200 Hz
- Duration per beep: 50ms
- Volume: -9 dB (subtle background)

---

### 4. Papers Cascade (Stage: Papers Flow)
**Trigger Point**: When papers start flying in
**Duration**: 2 seconds
**Audio Description**: Paper shuffling with increasing intensity
**Similar to**: Cards being dealt rapidly
**Example**: [Paper Shuffle](https://freesound.org/people/HighPixel/sounds/431174/)

```typescript
soundEffect: 'papers-cascade'
```

**Suggested Audio Characteristics**:
- Start: Single paper flutter
- Build to: Massive paper avalanche
- Texture: Crisp, bright
- Volume: -8 dB → -4 dB (crescendo)

---

### 5. Screening Stamps (Stage: Screening)
**Trigger Point**: When ACCEPTED/REJECTED stamps appear
**Duration**: 0.3 seconds per stamp
**Audio Description**: Rubber stamp thud with slight reverb
**Similar to**: Passport stamp or approval stamp
**Example**: [Stamp Sound](https://freesound.org/people/qubodup/sounds/222371/)

```typescript
soundEffect: 'screening-stamps'
```

**Suggested Audio Characteristics**:
- Dual stamps:
  - ACCEPTED: Higher pitch (800 Hz), satisfying "thunk"
  - REJECTED: Lower pitch (400 Hz), decisive "THUD"
- Quick attack, short decay
- Volume: -5 dB

**Sequence**:
```
0.0s: ACCEPTED stamp
0.3s: REJECTED stamp
```

---

### 6. Data Extraction (Stage: Extraction)
**Trigger Point**: When data fields start checking off
**Duration**: 0.1 seconds per checkbox
**Audio Description**: Tech beep sequence with rising pitch
**Similar to**: Computer processing sounds
**Example**: [Tech Beep](https://freesound.org/people/menegass/sounds/344502/)

```typescript
soundEffect: 'data-extraction'
```

**Suggested Audio Characteristics**:
- 8 sequential beeps
- Pitch progression: 600 Hz → 1200 Hz
- Timing: One every 0.2 seconds
- Final beep: Confirmation tone (lower, satisfied)
- Volume: -10 dB (subtle)

---

### 7. Chart Build (Stage: Analysis)
**Trigger Point**: When charts start animating
**Duration**: 3 seconds
**Audio Description**: Graph building sound with data points
**Similar to**: Analog modem syncing
**Example**: [Data Transfer](https://freesound.org/people/fins/sounds/146718/)

```typescript
soundEffect: 'chart-build'
```

**Suggested Audio Characteristics**:
- Glitchy, digital texture
- Rising pitch progression
- 4 distinct "sections" for 4 charts
- Build to satisfying resolution
- Volume: -7 dB

**Pattern**:
```
0.0s - 0.7s: Chart 1 (Forest Plot) - low tones
0.7s - 1.4s: Chart 2 (Funnel Plot) - mid tones
1.4s - 2.1s: Chart 3 (Meta-Regression) - high tones
2.1s - 3.0s: Chart 4 (Subgroup Analysis) - resolve
```

---

### 8. Report Complete (Stage: Report)
**Trigger Point**: When report generation finishes
**Duration**: 1 second
**Audio Description**: Success chime with shimmer
**Similar to**: Achievement unlocked, quest complete
**Example**: [Success Chime](https://freesound.org/people/LittleRobotSoundFactory/sounds/270404/)

```typescript
soundEffect: 'report-complete'
```

**Suggested Audio Characteristics**:
- Major chord progression: C → E → G → C'
- Bright, crystalline tone
- Shimmer tail with reverb
- Volume: -4 dB

---

### 9. Victory Fanfare (Stage: Celebration)
**Trigger Point**: When trophy appears
**Duration**: 2.5 seconds
**Audio Description**: Triumphant horns with confetti burst
**Similar to**: Sports victory, championship win
**Example**: [Victory Fanfare](https://freesound.org/people/FunWithSound/sounds/456966/)

```typescript
soundEffect: 'victory-fanfare'
```

**Suggested Audio Characteristics**:
- Orchestral brass section
- Rising melody with drum hits
- Confetti burst at 0.5s (whoosh + sparkle)
- Epic, cinematic
- Volume: -2 dB (loudest moment!)

**Composition**:
```
0.0s: Brass fanfare begins
0.5s: Confetti burst sound
1.0s: Drum hit
1.5s: Cymbal crash
2.0s: Resolve on major chord
```

---

### 10. Stats Reveal (Stage: Stats)
**Trigger Point**: When stats cards pop in
**Duration**: 0.3 seconds per stat
**Audio Description**: Counter ticking with pop reveal
**Similar to**: Scoreboard updating
**Example**: [Counter Tick](https://freesound.org/people/plasterbrain/sounds/423169/)

```typescript
soundEffect: 'stats-reveal'
```

**Suggested Audio Characteristics**:
- 4 sequential pops (one per stat)
- Each with:
  - Fast counter tick (100ms)
  - Pop reveal (pitched up as they progress)
- Timing: 0.2s between each
- Volume: -6 dB

**Sequence**:
```
0.0s: Stat 1 (10,000+) - 800 Hz pop
0.2s: Stat 2 (50,000+) - 900 Hz pop
0.4s: Stat 3 (2.5M) - 1000 Hz pop
0.6s: Stat 4 (99.2%) - 1200 Hz pop + sparkle
```

---

## Implementation

### Option 1: Howler.js (Recommended)

```bash
npm install howler
```

```typescript
// lib/demo-sounds.ts
import { Howl } from 'howler'

export const demoSounds = {
  'dramatic-intro': new Howl({
    src: ['/sounds/demo/dramatic-intro.mp3'],
    volume: 0.7,
    preload: true
  }),
  'project-start': new Howl({
    src: ['/sounds/demo/project-start.mp3'],
    volume: 0.5,
    preload: true
  }),
  'search-whoosh': new Howl({
    src: ['/sounds/demo/search-whoosh.mp3'],
    volume: 0.3,
    loop: true,
    preload: true
  }),
  'papers-cascade': new Howl({
    src: ['/sounds/demo/papers-cascade.mp3'],
    volume: 0.5,
    preload: true
  }),
  'screening-stamps': new Howl({
    src: ['/sounds/demo/screening-stamps.mp3'],
    volume: 0.6,
    preload: true
  }),
  'data-extraction': new Howl({
    src: ['/sounds/demo/data-extraction.mp3'],
    volume: 0.4,
    preload: true
  }),
  'chart-build': new Howl({
    src: ['/sounds/demo/chart-build.mp3'],
    volume: 0.5,
    preload: true
  }),
  'report-complete': new Howl({
    src: ['/sounds/demo/report-complete.mp3'],
    volume: 0.6,
    preload: true
  }),
  'victory-fanfare': new Howl({
    src: ['/sounds/demo/victory-fanfare.mp3'],
    volume: 0.8,
    preload: true
  }),
  'stats-reveal': new Howl({
    src: ['/sounds/demo/stats-reveal.mp3'],
    volume: 0.5,
    preload: true
  })
}

export function playDemoSound(soundName: string) {
  const sound = demoSounds[soundName]
  if (sound) {
    sound.play()
  }
}

export function stopDemoSound(soundName: string) {
  const sound = demoSounds[soundName]
  if (sound) {
    sound.stop()
  }
}

export function preloadDemoSounds() {
  Object.values(demoSounds).forEach(sound => sound.load())
}
```

**Integration in HighlightDemo.tsx**:

```typescript
import { useEffect } from 'react'
import { playDemoSound, stopDemoSound, preloadDemoSounds } from '@/lib/demo-sounds'

// Inside HighlightDemo component
useEffect(() => {
  // Preload sounds on mount
  preloadDemoSounds()
}, [])

useEffect(() => {
  // Play sound when stage changes
  if (currentStage.soundEffect) {
    playDemoSound(currentStage.soundEffect)
  }

  // Stop looping sounds on stage change
  return () => {
    if (currentStage.soundEffect === 'search-whoosh') {
      stopDemoSound('search-whoosh')
    }
  }
}, [currentStage])
```

---

### Option 2: Web Audio API (Advanced)

For more control and procedural generation:

```typescript
// lib/audio-engine.ts
class DemoAudioEngine {
  private audioContext: AudioContext
  private masterGain: GainNode

  constructor() {
    this.audioContext = new AudioContext()
    this.masterGain = this.audioContext.createGain()
    this.masterGain.connect(this.audioContext.destination)
    this.masterGain.gain.value = 0.7
  }

  playTone(frequency: number, duration: number, volume: number = 0.5) {
    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(this.masterGain)

    oscillator.frequency.value = frequency
    gainNode.gain.setValueAtTime(volume, this.audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(
      0.01,
      this.audioContext.currentTime + duration
    )

    oscillator.start(this.audioContext.currentTime)
    oscillator.stop(this.audioContext.currentTime + duration)
  }

  playSwoosh() {
    const startFreq = 200
    const endFreq = 2000
    const duration = 0.8

    for (let i = 0; i < 10; i++) {
      const time = (i / 10) * duration
      const freq = startFreq + (endFreq - startFreq) * (i / 10)
      setTimeout(() => this.playTone(freq, 0.1, 0.3), time * 1000)
    }
  }

  playDataExtraction() {
    const baseFreq = 600
    const steps = 8

    for (let i = 0; i < steps; i++) {
      const freq = baseFreq + (i * 75)
      setTimeout(() => {
        this.playTone(freq, 0.05, 0.2)
      }, i * 200)
    }
  }
}

export const audioEngine = new DemoAudioEngine()
```

---

## Sound Assets Directory Structure

```
public/
└── sounds/
    └── demo/
        ├── dramatic-intro.mp3
        ├── project-start.mp3
        ├── search-whoosh.mp3
        ├── papers-cascade.mp3
        ├── screening-stamps.mp3
        ├── data-extraction.mp3
        ├── chart-build.mp3
        ├── report-complete.mp3
        ├── victory-fanfare.mp3
        └── stats-reveal.mp3
```

---

## Free Sound Resources

### Recommended Sources

1. **Freesound.org** - Creative Commons sounds
   - Filter by CC0 (public domain)
   - High quality, diverse library
   - https://freesound.org

2. **BBC Sound Effects** - Free for personal/educational use
   - Professional quality
   - Curated library
   - https://sound-effects.bbcrewind.co.uk

3. **Zapsplat** - Free with attribution
   - Game and UI sounds
   - Regular updates
   - https://www.zapsplat.com

4. **Sonniss GameAudioGDC** - Annual free bundles
   - AAA game quality
   - Massive collections
   - https://sonniss.com/gameaudiogdc

---

## User Preferences

### Respect User Settings

```typescript
// hooks/useAudioPreference.ts
import { useState, useEffect } from 'react'

export function useAudioPreference() {
  const [audioEnabled, setAudioEnabled] = useState(true)

  useEffect(() => {
    // Check localStorage
    const savedPref = localStorage.getItem('demo-audio-enabled')
    if (savedPref !== null) {
      setAudioEnabled(savedPref === 'true')
    }

    // Check system preference
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (prefersReduced) {
      setAudioEnabled(false)
    }
  }, [])

  const toggleAudio = () => {
    const newValue = !audioEnabled
    setAudioEnabled(newValue)
    localStorage.setItem('demo-audio-enabled', String(newValue))
  }

  return { audioEnabled, toggleAudio }
}
```

**Add Audio Toggle to Demo UI**:

```tsx
import { Volume2, VolumeX } from 'lucide-react'
import { useAudioPreference } from '@/hooks/useAudioPreference'

// Inside HighlightDemo
const { audioEnabled, toggleAudio } = useAudioPreference()

// In control panel
<motion.button
  onClick={toggleAudio}
  className="p-4 bg-white/10 backdrop-blur-md border border-white/20 rounded-full"
  whileHover={{ scale: 1.1 }}
  whileTap={{ scale: 0.95 }}
>
  {audioEnabled ? (
    <Volume2 className="w-6 h-6 text-white" />
  ) : (
    <VolumeX className="w-6 h-6 text-white" />
  )}
</motion.button>
```

---

## Mobile Considerations

### Auto-play Restrictions

On iOS/Safari, audio cannot auto-play without user interaction:

```typescript
// Wait for user interaction before enabling audio
const [audioUnlocked, setAudioUnlocked] = useState(false)

const unlockAudio = () => {
  if (!audioUnlocked) {
    // Play silent sound to unlock audio context
    const silence = new Audio('data:audio/mp3;base64,//MkxAAHiAICWABElBeKPL/RANb2w+yiT1g/gTok//lP/W/l3h8QO/OCdCqCW2Cw//MkxAQHkAIWUAhEmAQXWUOFW2dxPu//9mr60ElY5sseQ+xxesmHKtZr7bsqqX2L//MkxAgFwAYiQAhEAC2hq22d3///9FTV6tA36JdgBJoOGgc+7qvqej5Zu7/7uI9l//MkxBQHAAYi8AhEAO193vt9KGOq+6qcT7hhfN5FTInmwk8RkqKImTM55pRQHQSq//MkxBsGkgoIAABHhTACIJLf99nVI///yuW1uBqWfEu7CgNPWGpUadBmZ////4sL//MkxCMHMAH6UABGwtJQnQwAB/DuFKQK6vu0amfHMdPEE//9f/92j//UuT//qKvLWJbf//MkxCwAAAAWUABEAJDf/8QAAB/8VeQAAQAAA//6K//4SsT//BQ0jP//TP/9KmP//MkxDIAAAG6UABEAAwXp//+qv//+qv//+K//5i//y///0f//zH/////+r////2f////MkxDYAAANKAAAAIADNJ////7t/////3///+6f////7pf////+K///+yv////9SP///y//MkxDsAAANoAAAAIAAFf//wv///9r/////+f///9X////7v///+r////6P///+yv///9v//MkxEIAAANoAAAAIAAD+K///wX///+r////+f///5f////3////+r////6P///8y////v//MkxEUAAANoAAAAIAACHp//V////////7/////+v////7L//kP///+r////6P////r////p//MkxEgAAANoAAAAIAAAf5/////7/////+f////6f////3////p////+P////0////+P//MkxEwAAANoAAAAIAAAf////////+v////5f////+P///6f////3////+P////6////P//MkxFAAAANoAAAAIAAAfT////+X/////8P/////p//////////5f/////5////+P////r//MkxFQAAANoAAAAIAAA/+X/////5f////+P/////////8X//////8P////+P////r////+//MkxFgAAANoAAAAIAAAAP////3//////5f/////3//////////+P////0////+P////p////MkxFwAAAG6AAAAIAAAA//////////p//////////6P////8P////6P/////v////6P////+f//MkxGAAAADKAAAAIAAAf////////8P/////+P////3//////////+P/////////+P////v////MkxGQAAADKAAAAIAAA//////////6P/////+P////////5f/////p//////////6P////r//MkxGgAAADKAAAAIAAA/////5f/////+P///////////+P/////+P////////6P/////+P////MkxGwAAAG6AAAAIAAAA//////////6P/////+P/////////5f/////p//////////6P////r//MkxHAAAAG6AAAAIAAAA/////5f/////+P///////////+P/////+P////////6P/////+P////')
    silence.play()
    setAudioUnlocked(true)
  }
}

// Call on Play button press
<button onClick={() => {
  unlockAudio()
  handlePlayPause()
}}>
  Play
</button>
```

---

## Testing

### Audio Testing Checklist

- [ ] All sound effects load without errors
- [ ] Sounds play at correct timing
- [ ] Volume levels are balanced
- [ ] No audio clipping or distortion
- [ ] Sounds work on Chrome, Firefox, Safari
- [ ] Sounds work on mobile (iOS, Android)
- [ ] Mute toggle functions correctly
- [ ] Sound preference persists across sessions
- [ ] Auto-play unlocking works on iOS
- [ ] No memory leaks from audio objects

---

## Production Checklist

- [ ] Compress audio files (MP3, 128kbps is sufficient)
- [ ] Add WebM alternatives for better browser support
- [ ] Implement lazy loading (load on first play)
- [ ] Add error handling for failed audio loads
- [ ] Respect user's reduced motion preference
- [ ] Provide visual-only fallback option
- [ ] Add attribution for CC-licensed sounds
- [ ] Test with screen readers (ensure sounds don't interfere)

---

## Questions?

Contact Visual Designer (Agent 3) for sound design questions or audio implementation support.

---

Happy sound designing! 🎵

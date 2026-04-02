export function useScrollReveal(delay = 0) {
  return {
    initial: {
      opacity: 0,
      y: 20
    },
    enter: {
      opacity: 1,
      y: 0,
      transition: {
        delay,
        duration: 400,
        ease: [0.16, 1, 0.3, 1]
      }
    }
  }
}

export function useStaggerReveal(itemIndex: number, baseDelay = 50) {
  return {
    initial: {
      opacity: 0,
      y: 20
    },
    enter: {
      opacity: 1,
      y: 0,
      transition: {
        delay: itemIndex * baseDelay,
        duration: 400,
        ease: [0.16, 1, 0.3, 1]
      }
    }
  }
}

export function useHoverScale() {
  return {
    hover: {
      scale: 1.02,
      transition: {
        duration: 200,
        ease: [0.34, 1.56, 0.64, 1]
      }
    }
  }
}

export function useCardReveal(delay = 0) {
  return {
    initial: {
      opacity: 0,
      y: 20,
      scale: 0.98
    },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        delay,
        duration: 400,
        ease: [0.16, 1, 0.3, 1]
      }
    }
  }
}

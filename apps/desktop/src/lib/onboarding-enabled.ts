export function isOnboardingEnabled(): boolean {
  return window.sciDesktop?.guestOnboardingEnabled === true
}

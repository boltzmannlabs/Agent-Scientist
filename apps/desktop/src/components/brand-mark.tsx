import { cn } from '@/lib/utils'

// Preserve layout while the approved SCI brand artwork is pending.
export function BrandMark({ className, ...props }: React.ComponentProps<'span'>) {
  return (
    <span aria-hidden="true" className={cn('inline-flex size-14 shrink-0 items-center justify-center', className)} {...props} />
  )
}

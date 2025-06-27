import React from 'react'

/**
 * Renders pagination controls with "Prev" and "Next" buttons and displays the current page out of the total pages.
 *
 * @param page - The current page number.
 * @param totalPages - The total number of available pages.
 * @param onPageChange - Callback invoked with the new page number when the page changes.
 * @returns A React element containing pagination controls.
 */
export function Pagination({ page, totalPages, onPageChange }: { page: number; totalPages: number; onPageChange: (p: number) => void }) {
  const prev = () => onPageChange(Math.max(1, page - 1))
  const next = () => onPageChange(Math.min(totalPages, page + 1))
  return (
    <div>
      <button onClick={prev} disabled={page === 1}>Prev</button>
      <span>{page} / {totalPages}</span>
      <button onClick={next} disabled={page === totalPages}>Next</button>
    </div>
  )
}

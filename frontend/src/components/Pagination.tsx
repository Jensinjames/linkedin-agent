import React from 'react'

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

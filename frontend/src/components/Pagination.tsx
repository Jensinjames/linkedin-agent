/**
 * Renders pagination controls with "Prev" and "Next" buttons and displays the current page out of the total pages.
 *
 * Calls the provided `onPageChange` callback with the new page number when navigation buttons are clicked, ensuring the page stays within valid bounds.
 *
 * @param page - The current page number
 * @param totalPages - The total number of pages available
 * @param onPageChange - Callback invoked with the new page number when the page changes
 * @returns A React element containing pagination controls
 */
export function Pagination({ page, totalPages, onPageChange }: { page: number; totalPages: number; onPageChange: (p: number) => void }) {
  const prev = () => onPageChange(Math.max(1, page - 1))
  const next = () => onPageChange(Math.min(totalPages, page + 1))
  
  return (
    <div className="pagination">
      <button 
        className="btn btn-secondary" 
        onClick={prev} 
        disabled={page === 1}
      >
        Previous
      </button>
      <span className="pagination-info">
        Page {page} of {totalPages}
      </span>
      <button 
        className="btn btn-secondary" 
        onClick={next} 
        disabled={page === totalPages}
      >
        Next
      </button>
    </div>
  )
}

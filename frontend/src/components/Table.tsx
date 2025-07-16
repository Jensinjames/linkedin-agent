export interface Column<T> {
  header: string
  accessor: keyof T
}

/**
 * Renders a generic HTML table based on provided column definitions and data.
 *
 * @param columns - Array of column definitions specifying headers and data accessors
 * @param data - Array of data objects to display as table rows
 * @returns A React element representing the rendered table
 */
export function Table<T>({ columns, data }: { columns: Column<T>[]; data: T[] }) {
  return (
    <table>
      <thead>
        <tr>
          {columns.map(col => (
            <th key={String(col.accessor)}>{col.header}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, i) => (
          <tr key={i}>
            {columns.map(col => (
              <td key={String(col.accessor)}>{String(row[col.accessor])}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}

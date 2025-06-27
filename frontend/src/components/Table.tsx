import React from 'react'

export interface Column<T> {
  header: string
  accessor: keyof T
}

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

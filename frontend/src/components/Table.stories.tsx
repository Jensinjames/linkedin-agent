import type { Meta, StoryObj } from '@storybook/react'
import { Table, type Column } from './Table'

interface Row {
  id: number
  name: string
}

const meta: Meta<typeof Table<Row>> = {
  component: Table,
}
export default meta

export const Basic: StoryObj<typeof Table<Row>> = {
  render: () => {
    const columns: Column<Row>[] = [
      { header: 'ID', accessor: 'id' },
      { header: 'Name', accessor: 'name' },
    ]
    const data: Row[] = [
      { id: 1, name: 'A' },
      { id: 2, name: 'B' },
    ]
    return <Table columns={columns} data={data} />
  },
}

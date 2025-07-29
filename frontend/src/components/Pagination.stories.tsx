import type { Meta, StoryObj } from '@storybook/react'
import { useState } from 'react'
import { Pagination } from './Pagination'

const meta: Meta<typeof Pagination> = {component: Pagination}
export default meta

function PaginationWrapper() {
    const [page, setPage] = useState(1)
    return <Pagination page={page} totalPages={5} onPageChange={setPage}/>
}

export const Basic: StoryObj<typeof Pagination> = {
    render: () => <PaginationWrapper/>,
}

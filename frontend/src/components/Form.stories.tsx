import type { Meta, StoryObj } from '@storybook/react'
import { Form, Field } from './Form'

const meta: Meta<typeof Form> = { component: Form }
export default meta

export const Basic: StoryObj<typeof Form> = {
  render: () => {
    const fields: Field[] = [
      { name: 'first', label: 'First Name' },
      { name: 'last', label: 'Last Name' },
    ]
    return <Form fields={fields} onSubmit={console.log} />
  },
}

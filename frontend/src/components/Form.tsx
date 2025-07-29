import type { FormEvent } from 'react'

export interface Field {
    name: string
    label: string
    type?: string
}

/**
 * Renders a dynamic form based on the provided field definitions and handles form submission.
 *
 * @param fields - Array of field definitions specifying the form's inputs
 * @param onSubmit - Callback invoked with an object mapping field names to their input values upon form submission
 */
export function Form({fields, onSubmit}: { fields: Field[]; onSubmit: (values: Record<string, string>) => void }) {
    const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault()
        const form = e.currentTarget
        const values: Record<string, string> = {}
        fields.forEach(f => {
            const input = form.elements.namedItem(f.name) as HTMLInputElement
            values[f.name] = input?.value || ''
        })
        onSubmit(values)
    }

    return (
        <form onSubmit={handleSubmit}>
            {fields.map(f => (
                <div key={f.name} className="form-group">
                    <label>
                        {f.label}
                        <input
                            className="form-input"
                            name={f.name}
                            type={f.type || 'text'}
                        />
                    </label>
                </div>
            ))}
            <button className="btn btn-primary" type="submit">
                Submit
            </button>
        </form>
    )
}

export default {
    template: `
        <q-list :bordered="bordered" :separator="separator" :padding="padding">
            <slot></slot>
        </q-list>
    `,
    props: {
        bordered: {
            type: Boolean,
            default: false
        },
        separator: {
            type: Boolean,
            default: false
        },
        padding: {
            type: Boolean,
            default: true
        }
    }
}

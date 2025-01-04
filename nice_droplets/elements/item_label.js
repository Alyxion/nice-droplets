export default {
    template: `
        <q-item-label>
            <slot>{{ text }}</slot>
        </q-item-label>
    `,
    props: {
        text: String
    }
}

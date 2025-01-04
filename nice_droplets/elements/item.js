export default {
    template: `
        <q-item :clickable="clickable" :disable="disable" :v-ripple="ripple">
            <slot name="before"></slot>
            <slot></slot>
            <slot name="after"></slot>
        </q-item>
    `,
    props: {
        clickable: {
            type: Boolean,
            default: true
        },
        disable: {
            type: Boolean,
            default: false
        },
        ripple: {
            type: Boolean,
            default: true
        }
    }
}

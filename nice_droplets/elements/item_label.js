export default {
    template: `
        <q-item-label
            :lines="lines"
            :caption="caption"
            :header="header"
            :overline="overline"
        >
            <slot>{{ text }}</slot>
        </q-item-label>
    `,
    props: {
        text: {
            type: String,
            default: ''
        },
        lines: {
            type: Number,
            default: undefined
        },
        caption: {
            type: Boolean,
            default: false
        },
        header: {
            type: Boolean,
            default: false
        },
        overline: {
            type: Boolean,
            default: false
        }
    },
    computed: {
        classes() {
            return {
                'ellipsis': this.lines === 1,
                'overflow-hidden': this.lines > 0
            }
        }
    },
    mounted() {
        if (this.lines > 1) {
            this.$el.style['-webkit-line-clamp'] = this.lines
            this.$el.style.display = '-webkit-box'
            this.$el.style['-webkit-box-orient'] = 'vertical'
        }
    }
}

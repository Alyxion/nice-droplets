export default {
    template: `
        <div class="q-item-label">
            <slot>{{ text }}</slot>
        </div>
    `,
    props: {
        text: String
    }
}

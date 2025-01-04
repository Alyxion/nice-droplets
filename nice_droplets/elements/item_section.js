export default {
    template: `
        <q-item-section :avatar="avatar" :thumbnail="thumbnail" :side="side" :top="top" :no-wrap="noWrap">
            <template v-if="overline">
                <q-item-label overline>{{ overline }}</q-item-label>
            </template>
            <template v-if="label">
                <q-item-label>{{ label }}</q-item-label>
            </template>
            <template v-if="caption">
                <q-item-label caption>{{ caption }}</q-item-label>
            </template>
            <slot></slot>
        </q-item-section>
    `,
    props: {
        avatar: Boolean,
        thumbnail: Boolean,
        side: Boolean,
        top: Boolean,
        noWrap: Boolean,
        overline: String,
        label: String,
        caption: String
    }
}

export default {
  template: `
    <div class="pdf-page-container" :style="{ width: width + 'px', height: height + 'px', position: 'relative', transform: 'scale(' + zoom + ')', transformOrigin: 'top center' }">
      <!-- Base image layer - this doesn't change when text blocks are updated -->
      <img :src="imgSrc" class="pdf-page-image" style="width: 100%; height: 100%; position: absolute; top: 0; left: 0; z-index: 1; user-select: none; pointer-events: none;">
      
      <!-- Slot for content (e.g., text overlay) -->
      <slot></slot>
    </div>
  `,
  props: {
    imgSrc: String,
    width: Number,
    height: Number,
    zoom: {
      type: Number,
      default: 1.0
    }
  },
  mounted() {
    this.$nextTick(() => {
      // Emit an event to notify parent components that the page is mounted
      this.$emit('page-mounted');
    });
  },
  updated() {
    this.$nextTick(() => {
      // Emit an event to notify parent components that the page is updated
      this.$emit('page-updated');
    });
  },
  watch: {
    zoom() {
      this.$nextTick(() => {
        // Emit an event to notify parent components that the zoom has changed
        this.$emit('zoom-changed', this.zoom);
      });
    }
  }
};

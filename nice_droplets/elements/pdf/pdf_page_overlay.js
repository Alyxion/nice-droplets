export default {
  template: `
    <div class="pdf-page-overlay" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:2;">
      <div class="pdf-interaction-layer" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:1;user-select:none;-webkit-user-select:none;"></div>

      <div v-for="(block, index) in textBlocks" :key="index" class="pdf-text-block" :style="computeTextStyle(block)">
        <span class="pdf-text-content" :style="computeContentStyle()">{{ block.text }}</span>
      </div>

      <div v-for="(overlay, idx) in overlays" :key="idx" :style="computeOverlayStyle(overlay)"></div>
    </div>
  `,
  props: {
    textBlocks: Array,
    showBoundings: Boolean,
    boundingStyle: String,
    overlays: {
      type: Array,
      default: () => []
    }
  },
  mounted() {
    this.$nextTick(() => this.adjustTextAndOverlayScaling());
  },
  updated() {
    this.$nextTick(() => this.adjustTextAndOverlayScaling());
  },
  watch: {
    textBlocks() { this.$nextTick(() => this.adjustTextAndOverlayScaling()); },
    showBoundings() { this.$forceUpdate(); },
    overlays() { this.$forceUpdate(); }
  },
  methods: {
    computeTextStyle(block) {
      return {
        position: 'absolute',
        left: block.x + 'px',
        top: block.y + 'px',
        width: block.width + 'px',
        height: block.height + 'px',
        margin: 0,
        padding: 0,
        overflow: 'hidden',
        border: this.showBoundings ? (this.boundingStyle || '1px solid red') : 'none',
        display: 'flex',
        alignItems: 'center',
        zIndex: 2
      };
    },
    computeContentStyle() {
      return {
        fontSize: 'inherit',
        fontFamily: 'inherit',
        lineHeight: 1,
        whiteSpace: 'nowrap',
        transformOrigin: 'left',
        width: 'auto',
        color: 'transparent',
        userSelect: 'text',
        cursor: 'text'
      };
    },
    computeOverlayStyle(overlay) {
      // overlay.x, y, width, height are in percent (0-100)
      const container = this.$el;
      const containerWidth = container ? container.offsetWidth : 1;
      const containerHeight = container ? container.offsetHeight : 1;
      let borderStyle = '2px solid ' + overlay.color;
      if (!overlay.color || overlay.color === 'none') {
        borderStyle = 'none';
      }
      let backgroundColor = 'rgba(0,0,0,0)';
      if (overlay.background_color && overlay.background_color !== 'none') {
        backgroundColor = overlay.background_color;
      }
      return {
        position: 'absolute',
        left: (overlay.x * containerWidth) + 'px',
        top: (overlay.y * containerHeight) + 'px',
        width: (overlay.width * containerWidth) + 'px',
        height: (overlay.height * containerHeight) + 'px',
        border: borderStyle,
        backgroundColor: backgroundColor,
        zIndex: 3,
        pointerEvents: 'none'
      };
    },
    adjustTextAndOverlayScaling() {
      try {
        this.adjustTextScaling();
      } catch (e) {
        // ignore
      }
    },
    adjustTextScaling() {
      // For each .pdf-text-block, scale the inner .pdf-text-content to fill the block horizontally
      this.$nextTick(() => {
        const blocks = this.$el.querySelectorAll('.pdf-text-block');
        blocks.forEach(block => {
          const content = block.querySelector('.pdf-text-content');
          if (content) {
            // Reset any previous transform
            content.style.transform = '';
            // Measure widths
            const blockWidth = block.offsetWidth;
            const contentWidth = content.scrollWidth;
            if (contentWidth > 0 && blockWidth > 0) {
              const scaleX = blockWidth / contentWidth;
              content.style.transform = `scaleX(${scaleX})`;
              content.style.transformOrigin = 'left';
            }
          }
        });
      });
    }
  }
};

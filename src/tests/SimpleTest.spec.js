import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent, h } from 'vue'

// Create a minimal test component
const TestComponent = defineComponent({
  name: 'TestComponent',
  setup() {
    return () => h('div', { class: 'test-component' }, 'Test Component')
  }
})

describe('Basic Vue Test Setup', () => {
  it('mounts a component correctly', () => {
    const wrapper = mount(TestComponent)
    expect(wrapper.find('.test-component').exists()).toBe(true)
    expect(wrapper.text()).toBe('Test Component')
  })

  it('handles basic assertions correctly', () => {
    expect(true).toBe(true)
    expect(1 + 1).toBe(2)
    expect({ name: 'test' }).toHaveProperty('name')
  })
}) 
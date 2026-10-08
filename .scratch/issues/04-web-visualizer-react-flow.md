# Issue 04: Interactive Web Visualizer (React Flow & Path Explorer)

## Status: Ready
**Milestone**: M3  
**Blocked by**: Issue 03 (Graph Builder)  

### Description
Implement the frontend application to visualize the generated curriculum graph interactively. Provide both an interactive node-link graph view and a linear roadmap view highlighting timestamps.

### Deliverables
1. Frontend setup with Next.js / Vite + React Flow + Tailwind CSS.
2. Custom nodes:
   - `SegmentNode`: Displays video title, segment label, and timestamp badge.
   - `ConceptNode`: Displays canonical concept tag and external badge if orphan.
3. Interactive path selector:
   - Selecting a target video highlights only its upstream ancestor tree.
   - Sidebar panel displaying the ordered step-by-step checklist with clickable YouTube timestamp links.

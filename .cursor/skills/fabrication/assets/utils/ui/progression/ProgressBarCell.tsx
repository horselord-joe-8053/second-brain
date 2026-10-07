/**
 * Single labeled progress bar cell with frosted tooltip — A1 dual-bar building block.
 * Expects host stylesheet classes ``f35-dual-progress-*`` and ``f35-progress-tooltip``.
 */
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { progressBarFillPct } from "./barFillRatio";

function ProgressTooltip({ title, body }: { title: string; body: string }) {
  return (
    <Box className="f35-progress-tooltip" role="tooltip">
      <Typography variant="caption" fontWeight={700} display="block">
        {title}
      </Typography>
      <Typography variant="caption" display="block">
        {body}
      </Typography>
    </Box>
  );
}

export type ProgressBarCellProps = {
  labelLeft: string;
  labelRight: string;
  inLevel: number;
  band: number;
  total: number;
  color: string;
  tooltipTitle: string;
  tooltipBody: string;
};

export function ProgressBarCell({
  labelLeft,
  labelRight,
  inLevel,
  band,
  total,
  color,
  tooltipTitle,
  tooltipBody,
}: ProgressBarCellProps) {
  const pct = progressBarFillPct(inLevel, band, total);
  return (
    <Box className="f35-dual-progress-cell">
      <Box className="f35-dual-progress-labels">
        <Typography variant="caption" noWrap>
          {labelLeft}
        </Typography>
        <Typography variant="caption" noWrap>
          {labelRight}
        </Typography>
      </Box>
      <Box className="f35-dual-progress-track" title={`${tooltipTitle} — ${tooltipBody}`}>
        <Box
          className="f35-dual-progress-fill"
          sx={{ width: `${pct}%`, backgroundColor: color }}
          data-testid="progress-fill"
        />
        <ProgressTooltip title={tooltipTitle} body={tooltipBody} />
      </Box>
    </Box>
  );
}

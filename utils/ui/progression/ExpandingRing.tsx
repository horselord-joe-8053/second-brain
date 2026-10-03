/**
 * Level-up expanding ring burst — shared by app CelebrationLayer and v9 canvas mockup.
 */
import {
  buildExpandingRingSpecs,
  EXPANDING_RING_CLASSES,
} from "./ringBurstSpec";
import {
  resolveRingAppearance,
  ringSpanClassName,
  ringSpanStyle,
} from "./ringColorTokens";

export type ExpandingRingProps = {
  /** Hex (``#2e7d32``) or token (``shiny-gold-1`` / ``#shiny-gold-1``). */
  color: string;
  className?: string;
  layerClassName?: string;
  "data-testid"?: string;
};

export function ExpandingRing({
  color,
  className,
  layerClassName,
  "data-testid": testId = "expanding-ring",
}: ExpandingRingProps) {
  const appearance = resolveRingAppearance(color);
  const specs = buildExpandingRingSpecs();
  const layerClass = [EXPANDING_RING_CLASSES.layer, layerClassName].filter(Boolean).join(" ");

  return (
    <div className={layerClass} aria-hidden data-testid={testId}>
      {specs.map((spec, i) => (
        <span
          key={i}
          className={ringSpanClassName(appearance, className)}
          style={ringSpanStyle(appearance, spec)}
          data-ring-color-kind={appearance.kind}
          data-ring-token={appearance.kind === "token" ? appearance.token : undefined}
        />
      ))}
    </div>
  );
}

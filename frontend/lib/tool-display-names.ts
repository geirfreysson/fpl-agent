/**
 * Maps tool names to user-friendly display names
 */
const TOOL_DISPLAY_NAMES: Record<string, string> = {
  // General tools
  help: "Looked at the FPL help guide",
  get_weather: "Checked weather",
  
  // Player search and analysis
  search_players: "Searched players",
  get_player_details: "Analyzed player details",
  get_player_form: "Analyzed player form",
  find_player_replacements: "Found player replacements",
  suggest_captain: "Analysed potential captains",
  
  // Fixture analysis
  get_easiest_fixtures: "Analyzed fixture difficulty",
  get_player_fixtures: "Checked player fixtures",
  
  // Price and budget analysis
  get_players_by_price_range: "Found players by price range",

  // Team analysis
  set_fpl_user_id: "Saved FPL entry ID",
  analyse_current_team: "Analyzed current team",
};

/**
 * Gets a friendly display name for a tool, falling back to the original name if no mapping exists
 */
export function getToolDisplayName(toolName: string): string {
  return TOOL_DISPLAY_NAMES[toolName] || `Used tool: ${toolName}`;
}
